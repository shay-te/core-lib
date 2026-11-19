"""Two methods of ONE Service instance, one with @Transaction() and one without, or both with it: run one after the
other, one calling the other, on two threads at once, and as asyncio workers. A transaction belongs to the thread that
opened it, never to the Service, so the methods never share a session unless one calls the other."""
import asyncio
import threading
import unittest

from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from core_lib.data_layers.service.service import Service
from tests.test_data.test_utils import connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 97
WAIT_SECONDS = 30
ASYNC_CALLS = 8


def _widget(name: str) -> dict:
    return {TransactionWidget.group_id.key: GROUP_ID, TransactionWidget.name.key: name}


class _WidgetService(Service):
    """One instance is shared by every test thread: it holds no transaction state of its own."""

    def __init__(self, transaction_widget_data_access: TransactionWidgetDataAccess):
        self._transaction_widget_data_access = transaction_widget_data_access

    @Transaction()
    def write_in_a_transaction(self, name: str, should_fail: bool = False, wait=None, before=None) -> object:
        if before is not None:
            before()
        self._transaction_widget_data_access.create(_widget(name))
        session = self._transaction_widget_data_access.current_session()
        if wait is not None:
            wait()
        if should_fail:
            raise LookupError('{} fails'.format(name))
        return session

    @Transaction()
    def write_then_call(self, name: str, other, should_fail: bool) -> tuple:
        self._transaction_widget_data_access.create(_widget(name))
        sessions = (self._transaction_widget_data_access.current_session(), other())
        if should_fail:
            raise LookupError('{} fails'.format(name))
        return sessions

    def write_plainly(self, name: str) -> object:
        self._transaction_widget_data_access.create(_widget(name))
        return self._transaction_widget_data_access.current_session()

    def read_plainly(self) -> list:
        return self._transaction_widget_data_access.names_in_group(GROUP_ID)


class TestTransactionServices(unittest.TestCase):

    def setUp(self):
        self.transaction_widget_data_access = TransactionWidgetDataAccess(connect_to_file_db(self))
        self.widget_service = _WidgetService(self.transaction_widget_data_access)

    def _names(self) -> list:
        return self.transaction_widget_data_access.names_in_group(GROUP_ID)

    def _run_in_thread(self, target) -> tuple:
        outcome = {}

        def run():
            try:
                outcome['result'] = target()
            except BaseException as error:
                outcome['error'] = error

        worker = threading.Thread(target=run)
        worker.start()
        return worker, outcome

    # one method with a transaction, one without

    def test_s1_one_after_the_other_on_one_thread_they_use_separate_sessions(self):
        transaction_session = self.widget_service.write_in_a_transaction('in-a-transaction')
        plain_session = self.widget_service.write_plainly('plain')

        self.assertIsNot(transaction_session, plain_session)
        self.assertIsNone(CoreLib.transaction_scope_registry.get())
        self.assertEqual(['in-a-transaction', 'plain'], self._names())

    def test_s2_a_plain_method_called_from_a_transaction_joins_it_and_rolls_back_with_it(self):
        with self.assertRaises(LookupError):
            self.widget_service.write_then_call('outer', lambda: self.widget_service.write_plainly('called'), True)
        after_failure = self._names()
        outer_session, called_session = self.widget_service.write_then_call(
            'outer', lambda: self.widget_service.write_plainly('called'), False)

        self.assertEqual([], after_failure)                     # the called plain write rolled back with it
        self.assertIs(outer_session, called_session)            # one session: it joined the transaction
        self.assertEqual(['called', 'outer'], self._names())

    def test_s3_on_two_threads_at_once_the_plain_method_never_sees_or_shares_the_transaction(self):
        written = threading.Event()
        looked = threading.Event()
        seen = {}

        def plain_thread():
            written.wait(WAIT_SECONDS)
            seen['names'] = self.widget_service.read_plainly()     # while the transaction is open
            seen['scope'] = CoreLib.transaction_scope_registry.get()
            looked.set()

        def wait_for_the_other_thread():
            written.set()
            looked.wait(WAIT_SECONDS)

        worker, _ = self._run_in_thread(plain_thread)
        with self.assertRaises(LookupError):
            self.widget_service.write_in_a_transaction('uncommitted', should_fail=True, wait=wait_for_the_other_thread)
        worker.join(WAIT_SECONDS)
        plain_session = self.widget_service.write_plainly('plain-after')

        self.assertEqual([], seen['names'])     # never saw the uncommitted row
        self.assertIsNone(seen['scope'])        # was never inside the other thread's transaction
        self.assertIsNotNone(plain_session)
        self.assertEqual(['plain-after'], self._names())

    # both methods with a transaction

    def test_s4_two_transactions_one_after_the_other_on_one_thread_are_separate(self):
        first = self.widget_service.write_in_a_transaction('first')
        with self.assertRaises(LookupError):
            self.widget_service.write_in_a_transaction('second', should_fail=True)

        self.assertIsNot(first, self.widget_service.write_in_a_transaction('third'))
        self.assertEqual(['first', 'third'], self._names())   # the second rolled back alone

    def test_s5_a_transaction_called_from_a_transaction_is_one_transaction(self):
        with self.assertRaises(LookupError):
            self.widget_service.write_then_call('outer', lambda: self.widget_service.write_in_a_transaction('inner'), True)
        after_failure = self._names()
        outer_session, inner_session = self.widget_service.write_then_call(
            'outer', lambda: self.widget_service.write_in_a_transaction('inner'), False)

        self.assertEqual([], after_failure)   # the inner transaction's write rolled back with the outer one
        self.assertIs(outer_session, inner_session)
        self.assertEqual(['inner', 'outer'], self._names())

    def test_s6_two_transactions_on_two_threads_at_once_never_share_a_session(self):
        first_written = threading.Event()
        second_inside = threading.Event()
        scopes = {}

        def second_starts():   # inside its own transaction, before writing (its write waits for the first's lock)
            scopes['second'] = CoreLib.transaction_scope_registry.get()
            second_inside.set()

        def first_waits_for_the_second_to_start():
            scopes['first'] = CoreLib.transaction_scope_registry.get()
            first_written.set()
            second_inside.wait(WAIT_SECONDS)   # now both transactions are open at the same time

        def second_thread():
            first_written.wait(WAIT_SECONDS)
            return self.widget_service.write_in_a_transaction('second', before=second_starts)

        worker, second_outcome = self._run_in_thread(second_thread)
        with self.assertRaises(LookupError):
            self.widget_service.write_in_a_transaction('first', should_fail=True,
                                                       wait=first_waits_for_the_second_to_start)
        worker.join(WAIT_SECONDS)

        self.assertIsNot(scopes['first'], scopes['second'])     # two transactions open at once, never one
        self.assertNotIn('error', second_outcome)
        self.assertEqual(['second'], self._names())             # the first rolled back alone, the second committed

    def test_s7_as_asyncio_workers_both_kinds_of_method_run_on_their_own(self):
        async def main():
            calls = []
            for i in range(ASYNC_CALLS):
                if i % 2:
                    calls.append(asyncio.to_thread(self.widget_service.write_plainly, 'plain-{}'.format(i)))
                else:
                    calls.append(asyncio.to_thread(self.widget_service.write_in_a_transaction, 'tx-{}'.format(i),
                                                   i % 4 == 0))
            return await asyncio.gather(*calls, return_exceptions=True)

        results = asyncio.run(main())

        sessions = [result for result in results if not isinstance(result, BaseException)]
        self.assertEqual(len(sessions), len({id(session) for session in sessions}))   # no two calls shared one
        failed = [result for result in results if isinstance(result, LookupError)]
        self.assertEqual(['tx-0 fails', 'tx-4 fails'], sorted(str(error) for error in failed))
        self.assertEqual(['plain-1', 'plain-3', 'plain-5', 'plain-7', 'tx-2', 'tx-6'], self._names())
