"""@Transaction() under hard conditions: forked and spawned processes, reused worker threads, many threads at once,
asyncio workers, blocks inside blocks, swallowed errors, after-commit work and colliding hashes."""
import asyncio
import multiprocessing
import os
import random
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from tests.test_data.recording_connection import EVENT_ENTER, EVENT_EXIT, EVENT_FLUSH, NO_ERROR
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import _connect_to_sqlite, connect_to_file_db, connect_to_mem_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 11
OTHER_GROUP_ID = 12
WAIT_SECONDS = 60
STRESS_THREADS = 24
STRESS_TRANSACTIONS = 40
ASYNC_WORKERS = 16
MAX_THREAD_ID_TRIES = 1000


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


def _spawned_writer(file_path: str, group_id: int, names: list, should_fail: bool, results):
    # runs in a spawned process: a fresh interpreter with its own registry, writing to the parent's sqlite file
    factory = _connect_to_sqlite({'protocol': 'sqlite', 'file': file_path})
    transaction_widget_data_access = TransactionWidgetDataAccess(factory)

    @Transaction()
    def write_group():
        for name in names:
            transaction_widget_data_access.create(_widget(name, group_id))
        if should_fail:
            raise RuntimeError('roll back')

    try:
        write_group()
        results.put((group_id, 'committed'))
    except RuntimeError:
        results.put((group_id, 'rolled back'))
    finally:
        factory.engine.dispose()


class _CollidingHashFactory(RecordingConnectionFactory):
    """A factory whose hash equals any other's: only `==` can tell them apart."""

    def __hash__(self) -> int:
        return 1


class TestTransactionHardCases(unittest.TestCase):

    def setUp(self):
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)

    def _names(self, group_id: int = GROUP_ID) -> list:
        return self.transaction_widget_data_access.names_in_group(group_id)

    def test_h1_a_block_inside_another_block_keeps_the_outer_blocks_rows(self):
        def rename_while_adding(row_id: int, group_id: int):
            with self.factory.get() as session:
                row = session.get(TransactionWidget, row_id)
                self.transaction_widget_data_access.create(_widget('added-inside', group_id))   # a block in this block
                row.name = 'renamed'

        rename_while_adding(self.transaction_widget_data_access.create(_widget('first')).id, GROUP_ID)
        outside = self._names()
        inside_id = self.transaction_widget_data_access.create(_widget('first', OTHER_GROUP_ID)).id
        Transaction()(rename_while_adding)(inside_id, OTHER_GROUP_ID)

        self.assertEqual(['added-inside', 'renamed'], outside)
        self.assertEqual(outside, self._names(OTHER_GROUP_ID))   # inside a transaction, the same rows as outside

    def test_h2_a_block_that_raises_saves_nothing_even_when_the_service_swallows_the_error(self):
        def add_then_fail():
            with self.factory.get() as session:
                session.add(TransactionWidget(group_id=GROUP_ID, name='from-the-failed-block'))
                raise ValueError('the block fails before its end')

        def swallow():
            try:
                add_then_fail()
            except ValueError:
                pass
            self.transaction_widget_data_access.create(_widget('after-the-failure'))

        swallow()
        outside = self._names()
        self.transaction_widget_data_access.delete_group(GROUP_ID)
        Transaction()(swallow)()

        self.assertEqual(['after-the-failure'], outside)
        self.assertEqual(outside, self._names())   # inside a transaction, the same rows as outside

    @unittest.skipUnless(hasattr(os, 'fork'), 'needs os.fork')
    def test_h3_a_process_forked_inside_a_transaction_is_not_inside_it(self):
        read_end, write_end = os.pipe()

        @Transaction()
        def fork_while_open():
            self.transaction_widget_data_access.create(_widget('parent-row'))
            child_pid = os.fork()
            if child_pid == 0:   # the child: report whether it found the parent's transaction, then leave at once
                os.close(read_end)
                os.write(write_end, b'inside' if CoreLib.transaction_registry.get() is not None else b'outside')
                os._exit(0)
            os.close(write_end)
            os.waitpid(child_pid, 0)
            return os.read(read_end, 16)

        child_saw = fork_while_open()
        os.close(read_end)

        self.assertEqual(b'outside', child_saw)
        self.assertEqual(['parent-row'], self._names())

    def test_h4_spawned_processes_writing_one_database_at_once_commit_or_roll_back_only_their_own(self):
        context = multiprocessing.get_context('spawn')
        results = context.Queue()
        file_path = self.factory.engine.url.database
        writers = [
            context.Process(target=_spawned_writer, args=(file_path, GROUP_ID, ['a1', 'a2', 'a3'], False, results)),
            context.Process(target=_spawned_writer, args=(file_path, OTHER_GROUP_ID, ['b1', 'b2'], True, results)),
            context.Process(target=_spawned_writer, args=(file_path, 13, ['c1'], False, results)),
        ]
        for writer in writers:
            writer.start()
        outcomes = dict(results.get(timeout=WAIT_SECONDS) for writer in writers)
        for writer in writers:
            writer.join(WAIT_SECONDS)
            self.assertEqual(0, writer.exitcode)

        self.assertEqual({GROUP_ID: 'committed', OTHER_GROUP_ID: 'rolled back', 13: 'committed'}, outcomes)
        self.assertEqual(['a1', 'a2', 'a3'], self._names())
        self.assertEqual([], self._names(OTHER_GROUP_ID))
        self.assertEqual(['c1'], self._names(13))

    def test_h5_a_reused_worker_thread_starts_clean_after_a_failed_transaction(self):
        recording_factory = RecordingConnectionFactory()

        @Transaction()
        def fail():
            with recording_factory.get():
                pass
            raise RuntimeError('fails')

        def plain_write():
            # no @Transaction(): must commit at once, never join a transaction left over from this thread's last task
            self.transaction_widget_data_access.create(_widget('plain-write'))
            return CoreLib.transaction_registry.get(), threading.get_ident()

        with ThreadPoolExecutor(max_workers=1) as pool:
            failed = pool.submit(fail)
            with self.assertRaises(RuntimeError):
                failed.result(WAIT_SECONDS)
            scope_after, thread_after = pool.submit(plain_write).result(WAIT_SECONDS)
            first_thread = pool.submit(threading.get_ident).result(WAIT_SECONDS)

        self.assertEqual(first_thread, thread_after)   # the same worker thread ran both tasks
        self.assertIsNone(scope_after)
        self.assertEqual(['plain-write'], self._names())
        self.assertIs(RuntimeError, recording_factory.created[0].exit_arguments()[0][0])

    def test_h5_a_new_thread_that_gets_a_finished_threads_id_starts_clean(self):
        failed_ids = set()
        looks = []

        def open_and_fail():
            failed_ids.add(threading.get_ident())
            try:
                Transaction()(self._raise)()
            except RuntimeError:
                pass

        def look():
            looks.append((threading.get_ident(), CoreLib.transaction_registry.get()))

        for i in range(MAX_THREAD_ID_TRIES):   # thread ids are reused once a thread ends; try until one is
            for target in (open_and_fail, look):
                worker = threading.Thread(target=target)
                worker.start()
                worker.join(WAIT_SECONDS)
            if looks[-1][0] in failed_ids:
                break

        self.assertIn(looks[-1][0], failed_ids)   # a thread really got a failed transaction's thread id
        self.assertEqual([None] * len(looks), [scope for _, scope in looks])

    def _raise(self):
        raise RuntimeError('fails')

    def test_h6_many_threads_many_transactions_with_random_failures(self):
        recording_factory = RecordingConnectionFactory()
        barrier = threading.Barrier(STRESS_THREADS, timeout=WAIT_SECONDS)
        outcomes = {}   # connection -> 'commit' | 'rollback', written by the thread that owns it
        errors = []

        @Transaction()
        def one_transaction(should_fail: bool):
            for i in range(3):
                with recording_factory.get():
                    pass
            connection = CoreLib.transaction_registry.get()._connections[recording_factory]
            outcomes[connection] = 'rollback' if should_fail else 'commit'
            if should_fail:
                raise RuntimeError('random failure')

        def run(seed: int):
            randomizer = random.Random(seed)
            try:
                barrier.wait()
                for i in range(STRESS_TRANSACTIONS):
                    try:
                        one_transaction(randomizer.random() < 0.3)
                    except RuntimeError:
                        pass
                    if CoreLib.transaction_registry.get() is not None:
                        errors.append('a transaction was left open on thread {}'.format(threading.get_ident()))
            except BaseException as error:
                errors.append(error)

        workers = [threading.Thread(target=run, args=(seed,)) for seed in range(STRESS_THREADS)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(WAIT_SECONDS)

        self.assertEqual([], errors)
        self.assertEqual(STRESS_THREADS * STRESS_TRANSACTIONS, len(recording_factory.created))
        for connection in recording_factory.created:
            self.assertEqual(1, len(connection.thread_ids()))   # never touched by a second thread
            self.assertEqual([EVENT_ENTER, EVENT_FLUSH] * 3 + [EVENT_EXIT], connection.events())
            [(exec_type, _, _)] = connection.exit_arguments()   # ended exactly once
            expected_type = None if outcomes[connection] == 'commit' else RuntimeError
            self.assertIs(expected_type, exec_type)
        self.assertEqual({}, CoreLib.transaction_registry._thread_to_transaction_scope)   # nothing left behind

    def test_h7_asyncio_workers_each_run_their_own_transaction(self):
        recording_factory = RecordingConnectionFactory()

        @Transaction()
        def one_transaction(number: int):
            with recording_factory.get():
                pass
            with recording_factory.get():
                pass
            return number, threading.get_ident()

        async def main():
            return await asyncio.gather(*[asyncio.to_thread(one_transaction, number) for number in range(ASYNC_WORKERS)])

        results = asyncio.run(main())

        self.assertEqual(list(range(ASYNC_WORKERS)), [number for number, _ in results])
        self.assertEqual(ASYNC_WORKERS, len(recording_factory.created))
        for connection in recording_factory.created:
            self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_ENTER, EVENT_FLUSH, EVENT_EXIT], connection.events())
            self.assertEqual([NO_ERROR], connection.exit_arguments())
        self.assertIsNone(CoreLib.transaction_registry.get())

    def test_h8_after_commit_callbacks_may_write_with_and_without_a_transaction_of_their_own(self):
        @Transaction()
        def write_in_a_callback_transaction():
            self.transaction_widget_data_access.create(_widget('callback-transaction', OTHER_GROUP_ID))

        def write_plainly():
            self.transaction_widget_data_access.create(_widget('callback-plain', OTHER_GROUP_ID))

        @Transaction()
        def main_write():
            self.transaction_widget_data_access.create(_widget('main'))
            CoreLib.transaction_registry.get().on_commit(write_in_a_callback_transaction)
            CoreLib.transaction_registry.get().on_commit(write_plainly)

        main_write()

        self.assertEqual(['main'], self._names())
        self.assertEqual(['callback-plain', 'callback-transaction'], self._names(OTHER_GROUP_ID))
        self.assertIsNone(CoreLib.transaction_registry.get())

    def test_h9_a_transaction_opened_inside_a_plain_block_uses_its_own_session(self):
        memory_factory = connect_to_mem_db()
        self.addCleanup(memory_factory.engine.dispose)
        memory_data_access = TransactionWidgetDataAccess(memory_factory)

        @Transaction()
        def transactional_write():
            memory_data_access.create(_widget('inside'))
            return memory_data_access.current_session()

        with memory_factory.get() as plain_session:
            plain_session.add(TransactionWidget(group_id=GROUP_ID, name='plain'))
            transaction_session = transactional_write()

        self.assertIsNot(plain_session, transaction_session)
        self.assertEqual(['inside', 'plain'], memory_data_access.names_in_group(GROUP_ID))

    def test_h10_a_thread_runs_a_new_transaction_after_a_commit_failure_and_after_a_failing_callback(self):
        failing_factory = RecordingConnectionFactory(commit_error=ConnectionError('commit fails'))
        recording_factory = RecordingConnectionFactory()

        @Transaction()
        def commit_fails():
            with failing_factory.get():
                pass

        @Transaction()
        def callback_fails():
            with recording_factory.get():
                pass
            CoreLib.transaction_registry.get().on_commit(self._raise)

        @Transaction()
        def works():
            with recording_factory.get():
                pass
            return CoreLib.transaction_registry.get()

        with self.assertRaises(ConnectionError):
            commit_fails()
        self.assertIsNone(CoreLib.transaction_registry.get())
        with self.assertRaises(RuntimeError):
            callback_fails()
        self.assertIsNone(CoreLib.transaction_registry.get())
        self.assertIsNotNone(works())

        self.assertEqual([[NO_ERROR], [NO_ERROR]], [connection.exit_arguments() for connection in recording_factory.created])
        self.assertIsNone(CoreLib.transaction_registry.get())

    def test_h11_factories_with_colliding_hashes_each_get_their_own_connection(self):
        first, second = _CollidingHashFactory(), _CollidingHashFactory()
        memory_factory = connect_to_mem_db()
        self.addCleanup(memory_factory.engine.dispose)

        @Transaction()
        def use_all():
            for factory in (first, second, first):
                with factory.get():
                    pass
            with memory_factory.get():
                pass
            return dict(CoreLib.transaction_registry.get()._connections)

        connections = use_all()

        self.assertEqual(hash(first), hash(second))
        self.assertEqual(3, len(connections))
        self.assertEqual([1, 1], [len(first.created), len(second.created)])
        self.assertIsNot(first.created[0], second.created[0])
