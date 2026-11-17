"""@Transaction() across threads: a scope is joined only from the thread that opened it, and
concurrent transactions never share a connection or see each other's uncommitted rows."""
import asyncio
import contextvars
import threading
import unittest

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.connection.transaction_decorator import Transaction
from core_lib.connection.transaction_scope import TransactionScope
from core_lib.core_lib import CoreLib
from tests.test_data.engine_event_counter import EngineEventCounter
from tests.test_data.recording_connection import EVENT_ENTER, EVENT_EXIT, EVENT_FLUSH, NO_ERROR
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess
from tests.test_data.transaction_widget_service import TRANSACTION_TEST_CACHE

WAIT_SECONDS = 10
THREAD_COUNT = 8
ITERATIONS = 5
WRITER_COUNT = 6
ROWS_PER_WRITER = 3
GROUP_ID = 4
CACHE_KEY_WORKER_VALUE = 'core_lib_test_transaction_worker_value'


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


class TestTransactionThreads(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CoreLib.cache_registry.register(TRANSACTION_TEST_CACHE, CacheHandlerRam())

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.unregister(TRANSACTION_TEST_CACHE)

    def setUp(self):
        # A sqlite FILE: an in-memory database is a different, empty database in every other thread.
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)
        CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).flush_all()

    def _start(self, target, *args):
        errors = []

        def run():
            try:
                target(*args)
            except BaseException as error:
                errors.append(error)

        worker = threading.Thread(target=run)
        worker.start()
        return worker, errors

    def _join(self, worker: threading.Thread):
        worker.join(WAIT_SECONDS)
        self.assertFalse(worker.is_alive())

    def _run_in_thread(self, function, copy_context: bool):
        outcome = {}

        def run():
            try:
                outcome['result'] = function()
            except BaseException as error:
                outcome['error'] = error

        if copy_context:
            # what asyncio.to_thread does, and what threading.Thread does by default from Python 3.14
            worker = threading.Thread(target=contextvars.copy_context().run, args=(run,))
        else:
            worker = threading.Thread(target=run)
        worker.start()
        self._join(worker)
        if 'error' in outcome:
            raise outcome['error']
        return outcome['result']

    def _assert_a_worker_thread_does_not_join(self, run_worker):
        factory = RecordingConnectionFactory()
        observed = {}

        def worker():
            observed['current_scope'] = CoreLib.transaction_registry.get()
            with factory.get():
                pass
            observed['worker_events_after_its_block'] = factory.created[1].events()

        @Transaction()
        def parent():
            with factory.get():
                pass
            observed['parent_scope'] = CoreLib.transaction_registry.get()
            run_worker(worker)
            observed['parent_events_after_worker'] = factory.created[0].events()

        parent()

        parent_connection, worker_connection = factory.created
        self.assertIsInstance(observed['parent_scope'], TransactionScope)
        self.assertIsNone(observed['current_scope'])  # the worker thread is not inside the parent's transaction
        self.assertEqual([EVENT_ENTER, EVENT_EXIT], observed['worker_events_after_its_block'])
        self.assertEqual([NO_ERROR], worker_connection.exit_arguments())
        self.assertTrue(worker_connection.thread_ids().isdisjoint(parent_connection.thread_ids()))
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH], observed['parent_events_after_worker'])
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_EXIT], parent_connection.events())

    def test_t1_concurrent_transactions_on_one_shared_function_never_share_a_connection(self):
        factory = RecordingConnectionFactory()
        barrier = threading.Barrier(THREAD_COUNT, timeout=WAIT_SECONDS)
        transaction = Transaction()

        def two_blocks():
            barrier.wait()  # all threads are inside their own transaction at once
            for i in range(2):
                with factory.get():
                    pass

        shared_function = transaction(two_blocks)

        def repeat():
            for i in range(ITERATIONS):
                shared_function()

        workers = [self._start(repeat) for i in range(THREAD_COUNT)]
        for worker, errors in workers:
            self._join(worker)
            self.assertEqual([], errors)

        self.assertEqual(THREAD_COUNT * ITERATIONS, len(factory.created))
        self.assertEqual(THREAD_COUNT * ITERATIONS, len({id(connection) for connection in factory.created}))
        connections_per_thread = {}
        for connection in factory.created:
            self.assertEqual(1, len(connection.thread_ids()))
            self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_ENTER, EVENT_FLUSH, EVENT_EXIT], connection.events())
            self.assertEqual([NO_ERROR], connection.exit_arguments())
            [thread_id] = connection.thread_ids()
            connections_per_thread[thread_id] = connections_per_thread.get(thread_id, 0) + 1
        self.assertEqual([ITERATIONS] * THREAD_COUNT, sorted(connections_per_thread.values()))
        self.assertEqual({}, vars(transaction))

    def test_t2_a_plain_worker_thread_commits_on_its_own(self):
        sessions = {}

        def worker_creates_its_row():
            sessions['worker'] = self.transaction_widget_data_access.current_session()
            self.transaction_widget_data_access.create(_widget('worker-row'))

        @Transaction()
        def parent():
            sessions['parent'] = self.transaction_widget_data_access.current_session()
            self._run_in_thread(worker_creates_its_row, copy_context=False)
            self.transaction_widget_data_access.create(_widget('parent-row'))
            raise RuntimeError('the parent fails')

        with self.assertRaises(RuntimeError):
            parent()

        self.assertEqual(['worker-row'], self.transaction_widget_data_access.names_in_group(GROUP_ID))
        self.assertIsNot(sessions['parent'], sessions['worker'])

    def test_t3_an_asyncio_to_thread_worker_does_not_join_the_transaction(self):
        self._assert_a_worker_thread_does_not_join(
            lambda worker: asyncio.run(asyncio.to_thread(worker)))

    def test_t4_a_thread_running_a_copied_context_does_not_join_either(self):
        self._assert_a_worker_thread_does_not_join(
            lambda worker: self._run_in_thread(worker, copy_context=True))

    def test_t5_a_copied_context_worker_runs_its_own_transaction(self):
        factory = RecordingConnectionFactory()
        observed = {}

        @Transaction()
        def worker_transaction():
            observed['worker_scope'] = CoreLib.transaction_registry.get()
            for i in range(2):
                with factory.get():
                    pass

        def worker():
            worker_transaction()
            observed['worker_events_when_done'] = factory.created[1].events()

        @Transaction()
        def parent():
            with factory.get():
                pass
            observed['parent_scope'] = CoreLib.transaction_registry.get()
            self._run_in_thread(worker, copy_context=True)
            observed['parent_scope_after_worker'] = CoreLib.transaction_registry.get()

        parent()

        parent_connection, worker_connection = factory.created
        self.assertIsInstance(observed['worker_scope'], TransactionScope)
        self.assertIsNot(observed['parent_scope'], observed['worker_scope'])
        self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_ENTER, EVENT_FLUSH, EVENT_EXIT],
                         observed['worker_events_when_done'])
        self.assertEqual([NO_ERROR], worker_connection.exit_arguments())
        self.assertIs(observed['parent_scope'], observed['parent_scope_after_worker'])
        self.assertEqual([NO_ERROR], parent_connection.exit_arguments())

    def test_t6_uncommitted_rows_are_invisible_to_another_thread(self):
        inserted = threading.Event()
        checked = threading.Event()
        waits = {}

        @Transaction()
        def insert_and_wait():
            for i in range(ROWS_PER_WRITER):
                self.transaction_widget_data_access.create(_widget('row-{}'.format(i)))
            inserted.set()
            waits['checked'] = checked.wait(WAIT_SECONDS)

        writer, errors = self._start(insert_and_wait)
        waits['inserted'] = inserted.wait(WAIT_SECONDS)
        count_before_commit = self.transaction_widget_data_access.count_all()
        checked.set()
        self._join(writer)
        count_after_commit = self.transaction_widget_data_access.count_all()

        self.assertEqual([], errors)
        self.assertEqual({'inserted': True, 'checked': True}, waits)
        self.assertEqual(0, count_before_commit)
        self.assertEqual(ROWS_PER_WRITER, count_after_commit)

    def test_t7_concurrent_writers_commit_or_roll_back_only_their_own_rows(self):
        barrier = threading.Barrier(WRITER_COUNT, timeout=WAIT_SECONDS)
        rolled_back = []

        @Transaction()
        def write_group(group_id: int):
            for i in range(ROWS_PER_WRITER):  # the first statement is a write (sqlite: one writer at a time)
                self.transaction_widget_data_access.create(_widget('row-{}'.format(i), group_id))
            if group_id % 2:
                raise RuntimeError('odd writer fails')

        def writer(group_id: int):
            barrier.wait()  # before the transaction, never while one holds the write lock
            try:
                write_group(group_id)
            except RuntimeError:
                rolled_back.append(group_id)

        with EngineEventCounter(self.factory.engine) as counter:
            workers = [self._start(writer, group_id) for group_id in range(1, WRITER_COUNT + 1)]
            for worker, errors in workers:
                self._join(worker)
                self.assertEqual([], errors)

        self.assertEqual([1, 3, 5], sorted(rolled_back))
        self.assertEqual(3, counter.commits)
        for group_id in range(1, WRITER_COUNT + 1):
            expected = [] if group_id % 2 else ['row-0', 'row-1', 'row-2']
            self.assertEqual(expected, self.transaction_widget_data_access.names_in_group(group_id))

    def test_t8_a_copied_context_worker_uses_the_cache_as_outside_a_transaction(self):
        values = ['first']

        @Cache(CACHE_KEY_WORKER_VALUE, handler_name=TRANSACTION_TEST_CACHE)
        def read_value():
            return values[0]

        def worker():
            first_read = read_value()
            values[0] = 'second'
            return first_read, read_value()

        @Transaction()
        def parent():
            return self._run_in_thread(worker, copy_context=True)

        self.assertEqual(('first', 'first'), parent())
        self.assertEqual('first', CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).get(CACHE_KEY_WORKER_VALUE))

    def test_t9_a_sync_transaction_called_inside_a_running_event_loop_commits(self):
        factory = RecordingConnectionFactory()

        @Transaction()
        def one_block():
            with factory.get():
                pass
            return 'committed'

        async def main():
            return one_block()

        self.assertEqual('committed', asyncio.run(main()))
        self.assertEqual([NO_ERROR], factory.created[0].exit_arguments())
        self.assertIsNone(CoreLib.transaction_registry.get())
