"""@Transaction() across processes: a forked child is never inside its parent's transaction and never ends it;
spawned and pooled processes writing one database each commit or roll back only their own rows."""
import multiprocessing
import os
import unittest
from concurrent.futures import ProcessPoolExecutor

from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from tests.test_data.test_utils import _connect_to_sqlite, connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 31
OTHER_GROUP_ID = 32
THIRD_GROUP_ID = 33
WAIT_SECONDS = 60
POOL_WORKERS = 3
POOL_TASKS = 9
CHILD_FOUND_KEY_ERROR = 7
CHILD_FOUND_ANOTHER_ERROR = 8
CHILD_GOT_THROUGH = 9

NEEDS_FORK = unittest.skipUnless(hasattr(os, 'fork'), 'needs os.fork')


def _widget(name: str, group_id: int) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


def _write_group(file_path: str, group_id: int, names: list, should_fail: bool) -> str:
    # runs in another process, with a factory of its own on the parent's sqlite file
    factory = _connect_to_sqlite({'protocol': 'sqlite', 'file': file_path})
    transaction_widget_data_access = TransactionWidgetDataAccess(factory)

    @Transaction()
    def write():
        for name in names:
            transaction_widget_data_access.create(_widget(name, group_id))
        if should_fail:
            raise RuntimeError('roll back')

    try:
        write()
        return 'committed'
    except RuntimeError:
        return 'rolled back'
    finally:
        factory.engine.dispose()


def _write_group_to_queue(file_path: str, group_id: int, names: list, should_fail: bool, results):
    results.put((group_id, _write_group(file_path, group_id, names, should_fail)))


class TestTransactionProcesses(unittest.TestCase):

    def setUp(self):
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)
        self.file_path = self.factory.engine.url.database

    def _names(self, group_id: int) -> list:
        return self.transaction_widget_data_access.names_in_group(group_id)

    @NEEDS_FORK
    def test_p1_a_process_forked_inside_a_transaction_is_not_inside_it(self):
        read_end, write_end = os.pipe()

        @Transaction()
        def fork_while_open():
            self.transaction_widget_data_access.create(_widget('parent-row', GROUP_ID))
            child_pid = os.fork()
            if child_pid == 0:   # the child: report whether it found the parent's transaction, then leave at once
                os.close(read_end)
                os.write(write_end, b'inside' if CoreLib.transaction_scope_registry.get() is not None else b'outside')
                os._exit(0)
            os.close(write_end)
            os.waitpid(child_pid, 0)
            return os.read(read_end, 16)

        child_saw = fork_while_open()
        os.close(read_end)

        self.assertEqual(b'outside', child_saw)
        self.assertEqual(['parent-row'], self._names(GROUP_ID))

    @NEEDS_FORK
    def test_p2_a_forked_child_that_returns_through_the_decorator_never_ends_the_parents_transaction(self):
        fork_result = {}

        @Transaction()
        def write_and_fork():
            self.transaction_widget_data_access.create(_widget('parent-row', GROUP_ID))
            fork_result['pid'] = os.fork()
            return fork_result['pid']

        try:
            child_pid = write_and_fork()
        except BaseException as error:
            if fork_result.get('pid') == 0:   # the child: the decorator refused to end a transaction it does not own
                os._exit(CHILD_FOUND_KEY_ERROR if isinstance(error, KeyError) else CHILD_FOUND_ANOTHER_ERROR)
            raise
        if child_pid == 0:
            os._exit(CHILD_GOT_THROUGH)   # the child must never reach here: it would have ended the parent's session
        _, status = os.waitpid(child_pid, 0)

        self.assertEqual(CHILD_FOUND_KEY_ERROR, os.waitstatus_to_exitcode(status))
        self.assertEqual(['parent-row'], self._names(GROUP_ID))   # committed once, by the parent

    @NEEDS_FORK
    def test_p3_a_forked_child_runs_transactions_of_its_own(self):
        context = multiprocessing.get_context('fork')
        results = context.Queue()
        writers = [
            context.Process(target=_write_group_to_queue, args=(self.file_path, GROUP_ID, ['f1', 'f2'], False, results)),
            context.Process(target=_write_group_to_queue, args=(self.file_path, OTHER_GROUP_ID, ['g1'], True, results)),
        ]
        for writer in writers:
            writer.start()
        outcomes = dict(results.get(timeout=WAIT_SECONDS) for writer in writers)
        for writer in writers:
            writer.join(WAIT_SECONDS)

        self.assertEqual({GROUP_ID: 'committed', OTHER_GROUP_ID: 'rolled back'}, outcomes)
        self.assertEqual(['f1', 'f2'], self._names(GROUP_ID))
        self.assertEqual([], self._names(OTHER_GROUP_ID))

    def test_p4_spawned_processes_writing_one_database_at_once_commit_or_roll_back_only_their_own(self):
        context = multiprocessing.get_context('spawn')
        results = context.Queue()
        writers = [
            context.Process(target=_write_group_to_queue, args=(self.file_path, GROUP_ID, ['a1', 'a2', 'a3'], False, results)),
            context.Process(target=_write_group_to_queue, args=(self.file_path, OTHER_GROUP_ID, ['b1', 'b2'], True, results)),
            context.Process(target=_write_group_to_queue, args=(self.file_path, THIRD_GROUP_ID, ['c1'], False, results)),
        ]
        for writer in writers:
            writer.start()
        outcomes = dict(results.get(timeout=WAIT_SECONDS) for writer in writers)
        for writer in writers:
            writer.join(WAIT_SECONDS)
            self.assertEqual(0, writer.exitcode)

        self.assertEqual({GROUP_ID: 'committed', OTHER_GROUP_ID: 'rolled back', THIRD_GROUP_ID: 'committed'}, outcomes)
        self.assertEqual(['a1', 'a2', 'a3'], self._names(GROUP_ID))
        self.assertEqual([], self._names(OTHER_GROUP_ID))
        self.assertEqual(['c1'], self._names(THIRD_GROUP_ID))

    def test_p5_a_process_pool_runs_many_transactions_and_keeps_only_the_committed_ones(self):
        tasks = [(100 + number, ['task-{}'.format(number)], number % 3 == 0) for number in range(POOL_TASKS)]

        with ProcessPoolExecutor(POOL_WORKERS, mp_context=multiprocessing.get_context('spawn')) as pool:
            futures = [pool.submit(_write_group, self.file_path, group_id, names, should_fail)
                       for group_id, names, should_fail in tasks]
            outcomes = [future.result(WAIT_SECONDS) for future in futures]

        self.assertEqual(['rolled back' if should_fail else 'committed' for _, _, should_fail in tasks], outcomes)
        for group_id, names, should_fail in tasks:
            self.assertEqual([] if should_fail else names, self._names(group_id))

    def test_p6_the_parent_is_untouched_by_a_child_that_fails(self):
        context = multiprocessing.get_context('spawn')
        results = context.Queue()

        @Transaction()
        def parent_writes_after_the_child():
            child = context.Process(target=_write_group_to_queue,
                                    args=(self.file_path, OTHER_GROUP_ID, ['child'], True, results))
            child.start()
            outcome = results.get(timeout=WAIT_SECONDS)   # the child finished (it wrote nothing: it rolled back)
            child.join(WAIT_SECONDS)
            self.transaction_widget_data_access.create(_widget('parent', GROUP_ID))
            return outcome

        self.assertEqual((OTHER_GROUP_ID, 'rolled back'), parent_writes_after_the_child())
        self.assertEqual(['parent'], self._names(GROUP_ID))
        self.assertEqual([], self._names(OTHER_GROUP_ID))
