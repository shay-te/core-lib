"""@Transaction() under load: hundreds of databases in one transaction, thousands of transactions in a row, many
threads each running many transactions, many threads on one shared database, more transactions at once than the
connection pool holds, and no transaction, scope or connection left behind afterwards."""
import gc
import random
import threading
import time
import unittest
import weakref

from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from tests.test_data.engine_event_counter import EngineEventCounter
from tests.test_data.recording_connection import NO_ERROR
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_file_db, connect_to_mem_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 51
WAIT_SECONDS = 120
DATABASES_IN_ONE_TRANSACTION = 200
TRANSACTIONS_IN_A_ROW = 2000
SCOPE_THREADS = 64
SCOPES_PER_THREAD = 200
OWN_DATABASE_THREADS = 16
TRANSACTIONS_PER_OWN_DATABASE = 50
SHARED_DATABASE_THREADS = 12
TRANSACTIONS_PER_SHARED_THREAD = 20
POOL_THREADS = 40
TRANSACTIONS_PER_POOL_THREAD = 5
LEAK_TRANSACTIONS = 1000
FAILURE_RATE = 0.25


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


class TestTransactionLoad(unittest.TestCase):

    def _run_threads(self, targets: list) -> list:
        errors = []

        def run(target):
            try:
                target()
            except BaseException as error:
                errors.append(error)

        workers = [threading.Thread(target=run, args=(target,)) for target in targets]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(WAIT_SECONDS)
            self.assertFalse(worker.is_alive())
        return errors

    def _memory_data_accesses(self, count: int) -> list:
        data_accesses = []
        for i in range(count):
            factory = connect_to_mem_db()
            self.addCleanup(factory.engine.dispose)
            data_accesses.append(TransactionWidgetDataAccess(factory))
        return data_accesses

    def test_l1_hundreds_of_databases_in_one_transaction_commit_together_and_roll_back_together(self):
        data_accesses = self._memory_data_accesses(DATABASES_IN_ONE_TRANSACTION)

        @Transaction()
        def write_to_every_database(name: str, should_fail: bool):
            for data_access in data_accesses:
                data_access.create(_widget(name))
            sessions = {id(data_access.current_session()) for data_access in data_accesses}
            if should_fail:
                raise RuntimeError('roll every database back')
            return sessions

        sessions = write_to_every_database('committed', False)
        with self.assertRaises(RuntimeError):
            write_to_every_database('rolled-back', True)

        self.assertEqual(DATABASES_IN_ONE_TRANSACTION, len(sessions))   # one session per database, none shared
        self.assertEqual([['committed']] * DATABASES_IN_ONE_TRANSACTION,
                         [data_access.names_in_group(GROUP_ID) for data_access in data_accesses])

    def test_l2_thousands_of_transactions_in_a_row_each_commit_or_roll_back_on_their_own(self):
        [data_access] = self._memory_data_accesses(1)
        randomizer = random.Random(2)
        expected = []

        @Transaction()
        def one_transaction(number: int, should_fail: bool):
            data_access.create(_widget('row-{:05d}'.format(number)))
            if should_fail:
                raise RuntimeError('roll back')

        for number in range(TRANSACTIONS_IN_A_ROW):
            should_fail = randomizer.random() < FAILURE_RATE
            try:
                one_transaction(number, should_fail)
                expected.append('row-{:05d}'.format(number))
            except RuntimeError:
                pass

        self.assertEqual(expected, data_access.names_in_group(GROUP_ID))
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_l3_many_threads_open_many_scopes_and_never_share_one(self):
        recording_factory = RecordingConnectionFactory()
        scopes_by_thread = {}
        start = threading.Barrier(SCOPE_THREADS, timeout=WAIT_SECONDS)

        @Transaction()
        def one_scope():
            with recording_factory.get():
                pass
            return CoreLib.transaction_scope_registry.get()

        def run():
            start.wait()
            scopes_by_thread[threading.get_ident()] = [id(one_scope()) for i in range(SCOPES_PER_THREAD)]

        errors = self._run_threads([run] * SCOPE_THREADS)

        self.assertEqual([], errors)
        self.assertEqual(SCOPE_THREADS * SCOPES_PER_THREAD, len(recording_factory.created))
        self.assertEqual([[NO_ERROR]] * len(recording_factory.created),
                         [connection.exit_arguments() for connection in recording_factory.created])
        for connection in recording_factory.created:
            self.assertEqual(1, len(connection.thread_ids()))
        self.assertEqual({}, CoreLib.transaction_scope_registry._thread_to_transaction_scope)

    def test_l4_many_threads_each_on_its_own_database_with_random_failures(self):
        data_accesses = [TransactionWidgetDataAccess(connect_to_file_db(self)) for i in range(OWN_DATABASE_THREADS)]
        expected = {}

        def run(index: int):
            data_access = data_accesses[index]
            randomizer = random.Random(index)
            committed = []

            @Transaction()
            def two_rows(number: int, should_fail: bool):
                data_access.create(_widget('a-{:03d}'.format(number)))
                data_access.create(_widget('b-{:03d}'.format(number)))
                if should_fail:
                    raise RuntimeError('roll back')

            for number in range(TRANSACTIONS_PER_OWN_DATABASE):
                try:
                    two_rows(number, randomizer.random() < FAILURE_RATE)
                    committed += ['a-{:03d}'.format(number), 'b-{:03d}'.format(number)]
                except RuntimeError:
                    pass
            expected[index] = sorted(committed)

        errors = self._run_threads([lambda index=index: run(index) for index in range(OWN_DATABASE_THREADS)])

        self.assertEqual([], errors)
        for index, data_access in enumerate(data_accesses):
            self.assertEqual(expected[index], data_access.names_in_group(GROUP_ID))

    def test_l5_many_threads_writing_one_shared_database_keep_exactly_the_committed_rows(self):
        factory = connect_to_file_db(self)
        data_access = TransactionWidgetDataAccess(factory)
        committed = []
        committed_lock = threading.Lock()

        def run(index: int):
            randomizer = random.Random(100 + index)

            @Transaction()
            def two_rows(number: int, should_fail: bool):
                data_access.create(_widget('t{:02d}-{:02d}-a'.format(index, number)))
                data_access.create(_widget('t{:02d}-{:02d}-b'.format(index, number)))
                if should_fail:
                    raise RuntimeError('roll back')

            for number in range(TRANSACTIONS_PER_SHARED_THREAD):
                try:
                    two_rows(number, randomizer.random() < FAILURE_RATE)
                    with committed_lock:
                        committed.extend(['t{:02d}-{:02d}-a'.format(index, number), 't{:02d}-{:02d}-b'.format(index, number)])
                except RuntimeError:
                    pass

        with EngineEventCounter(factory.engine) as counter:
            errors = self._run_threads([lambda index=index: run(index) for index in range(SHARED_DATABASE_THREADS)])

        self.assertEqual([], errors)   # no 'database is locked': each writer waited its turn
        self.assertEqual(sorted(committed), data_access.names_in_group(GROUP_ID))
        transactions = SHARED_DATABASE_THREADS * TRANSACTIONS_PER_SHARED_THREAD
        self.assertEqual(transactions, counter.checkouts)   # one connection per transaction, never per block
        self.assertEqual(counter.checkouts, counter.checkins)

    def test_l6_more_transactions_at_once_than_the_pool_holds_all_finish_and_give_every_connection_back(self):
        factory = connect_to_file_db(self)
        data_access = TransactionWidgetDataAccess(factory)
        data_access.create(_widget('seed'))
        start = threading.Barrier(POOL_THREADS, timeout=WAIT_SECONDS)

        @Transaction()
        def three_reads():
            for i in range(3):
                data_access.names_in_group(GROUP_ID)
            time.sleep(0.001)   # hold the connection a moment, so many transactions are open at once

        def run():
            start.wait()
            for i in range(TRANSACTIONS_PER_POOL_THREAD):
                three_reads()

        with EngineEventCounter(factory.engine) as counter:
            errors = self._run_threads([run] * POOL_THREADS)

        self.assertEqual([], errors)
        self.assertEqual(POOL_THREADS * TRANSACTIONS_PER_POOL_THREAD, counter.checkouts)
        self.assertEqual(counter.checkouts, counter.checkins)   # every connection went back to the pool

    def test_l7_thousands_of_transactions_leave_no_scope_or_connection_behind(self):
        [data_access] = self._memory_data_accesses(1)
        scopes = []
        connections = []

        @Transaction()
        def one_transaction(number: int):
            data_access.create(_widget('row-{:04d}'.format(number)))
            scopes.append(weakref.ref(CoreLib.transaction_scope_registry.get()))
            [connection] = CoreLib.transaction_scope_registry.get().connections.values()
            connections.append(weakref.ref(connection))

        for number in range(LEAK_TRANSACTIONS):
            one_transaction(number)
        gc.collect()

        self.assertEqual([], [scope for scope in scopes if scope() is not None])
        self.assertEqual([], [connection for connection in connections if connection() is not None])
        self.assertIsNone(CoreLib.transaction_scope_registry.get())
        self.assertEqual(LEAK_TRANSACTIONS, data_access.count_all())
