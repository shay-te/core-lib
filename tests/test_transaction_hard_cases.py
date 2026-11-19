"""@Transaction() under hard conditions: reused worker threads, many threads at once, blocks inside blocks,
swallowed errors, failing commits across databases, after-commit work, deep nesting and colliding hashes.
Processes: test_transaction_processes.py; asyncio: test_transaction_asyncio.py."""
import random
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

from sqlalchemy import text, update
from sqlalchemy.exc import IntegrityError

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import ResultToDict
from tests.test_data.engine_event_counter import EngineEventCounter
from tests.test_data.recording_connection import EVENT_ENTER, EVENT_EXIT, EVENT_FLUSH, EVENT_RELEASE, NO_ERROR
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_file_db, connect_to_mem_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 11
OTHER_GROUP_ID = 12
WAIT_SECONDS = 60
STRESS_THREADS = 24
STRESS_TRANSACTIONS = 40
MAX_THREAD_ID_TRIES = 1000
MANY_BLOCKS = 2000
RECURSION_DEPTH = 50
NESTING_THREADS = 8
CALLBACK_CHAIN = 3
HARD_CASE_CACHE = 'core_lib_test_transaction_hard_case_cache'
CACHE_KEY_VALUE = 'core_lib_test_transaction_hard_case_value'


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


class _EqualityWithoutHashFactory(RecordingConnectionFactory):
    """Defines `__eq__` and no `__hash__`, so Python makes it unhashable."""

    def __eq__(self, other) -> bool:
        return other is self


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
            return CoreLib.transaction_scope_registry.get(), threading.get_ident()

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
            looks.append((threading.get_ident(), CoreLib.transaction_scope_registry.get()))

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
            connection = CoreLib.transaction_scope_registry.get().connections[recording_factory]
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
                    if CoreLib.transaction_scope_registry.get() is not None:
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
            self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_RELEASE] * 3 + [EVENT_EXIT], connection.events())
            [(exec_type, _, _)] = connection.exit_arguments()   # ended exactly once
            expected_type = None if outcomes[connection] == 'commit' else RuntimeError
            self.assertIs(expected_type, exec_type)
        self.assertEqual({}, CoreLib.transaction_scope_registry._thread_to_transaction_scope)   # nothing left behind

    def test_h8_after_commit_callbacks_may_write_with_and_without_a_transaction_of_their_own(self):
        @Transaction()
        def write_in_a_callback_transaction():
            self.transaction_widget_data_access.create(_widget('callback-transaction', OTHER_GROUP_ID))

        def write_plainly():
            self.transaction_widget_data_access.create(_widget('callback-plain', OTHER_GROUP_ID))

        @Transaction()
        def main_write():
            self.transaction_widget_data_access.create(_widget('main'))
            CoreLib.transaction_scope_registry.get().on_commit.append(write_in_a_callback_transaction)
            CoreLib.transaction_scope_registry.get().on_commit.append(write_plainly)

        main_write()

        self.assertEqual(['main'], self._names())
        self.assertEqual(['callback-plain', 'callback-transaction'], self._names(OTHER_GROUP_ID))
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

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
            CoreLib.transaction_scope_registry.get().on_commit.append(self._raise)

        @Transaction()
        def works():
            with recording_factory.get():
                pass
            return CoreLib.transaction_scope_registry.get()

        with self.assertRaises(ConnectionError):
            commit_fails()
        self.assertIsNone(CoreLib.transaction_scope_registry.get())
        with self.assertRaises(RuntimeError):
            callback_fails()
        self.assertIsNone(CoreLib.transaction_scope_registry.get())
        self.assertIsNotNone(works())

        self.assertEqual([[NO_ERROR], [NO_ERROR]], [connection.exit_arguments() for connection in recording_factory.created])
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

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
            return dict(CoreLib.transaction_scope_registry.get().connections)

        connections = use_all()

        self.assertEqual(hash(first), hash(second))
        self.assertEqual(3, len(connections))
        self.assertEqual([1, 1], [len(first.created), len(second.created)])
        self.assertIsNot(first.created[0], second.created[0])

    def test_h12_three_databases_where_the_second_commit_fails(self):
        factories = [connect_to_mem_db() for i in range(3)]
        for factory in factories:
            self.addCleanup(factory.engine.dispose)
        data_accesses = [TransactionWidgetDataAccess(factory) for factory in factories]
        commit_failure = ConnectionError('the second database is gone')
        callbacks_run = []

        @Transaction()
        def write_each():
            for data_access in data_accesses:
                data_access.create(_widget('row'))
            data_accesses[1].current_session().commit = mock.Mock(side_effect=commit_failure)
            CoreLib.transaction_scope_registry.get().on_commit.append(lambda: callbacks_run.append('ran'))

        with self.assertRaises(ConnectionError) as raised:
            write_each()

        self.assertIs(commit_failure, raised.exception)
        # no two-phase commit: the first database committed before the second failed; the third rolled back
        self.assertEqual([['row'], [], []], [data_access.names_in_group(GROUP_ID) for data_access in data_accesses])
        self.assertEqual([], callbacks_run)
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_h13_thousands_of_blocks_use_one_connection_and_one_commit(self):
        @Transaction()
        def many_blocks():
            for i in range(MANY_BLOCKS):
                self.transaction_widget_data_access.create(_widget('row-{}'.format(i)))

        with EngineEventCounter(self.factory.engine) as counter:
            many_blocks()

        self.assertEqual((1, 1, 1), (counter.commits, counter.checkouts, counter.checkins))
        self.assertEqual(MANY_BLOCKS, self.transaction_widget_data_access.count_all())

    def test_h14_an_interrupt_in_an_after_commit_callback_comes_after_the_commit(self):
        def interrupt():
            raise KeyboardInterrupt()

        @Transaction()
        def write_then_register():
            self.transaction_widget_data_access.create(_widget('committed-first'))
            CoreLib.transaction_scope_registry.get().on_commit.append(interrupt)

        with self.assertRaises(KeyboardInterrupt):
            write_then_register()

        self.assertEqual(['committed-first'], self._names())
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_h15_a_thread_started_inside_a_transaction_that_outlives_it_writes_on_its_own(self):
        transaction_ended = threading.Event()
        seen = {}

        def outlive():
            transaction_ended.wait(WAIT_SECONDS)
            seen['scope'] = CoreLib.transaction_scope_registry.get()
            self.transaction_widget_data_access.create(_widget('written-later'))

        @Transaction()
        def start_a_worker():
            self.transaction_widget_data_access.create(_widget('in-the-transaction'))
            worker = threading.Thread(target=outlive)
            worker.start()
            return worker

        worker = start_a_worker()
        transaction_ended.set()
        worker.join(WAIT_SECONDS)

        self.assertIsNone(seen['scope'])
        self.assertEqual(['in-the-transaction', 'written-later'], self._names())

    def test_h16_a_transaction_that_touches_no_database_still_runs_its_after_commit_callbacks(self):
        callbacks_run = []

        @Transaction()
        def only_a_callback():
            CoreLib.transaction_scope_registry.get().on_commit.append(lambda: callbacks_run.append('ran'))

        only_a_callback()

        self.assertEqual(['ran'], callbacks_run)

    def test_h17_a_deep_recursion_of_transactions_writes_on_one_connection_and_commits_once(self):
        @Transaction()
        def write_level(depth: int):
            self.transaction_widget_data_access.create(_widget('level-{:03d}'.format(depth)))
            if depth < RECURSION_DEPTH:
                write_level(depth + 1)

        with EngineEventCounter(self.factory.engine) as counter:
            write_level(1)

        self.assertEqual((1, 1), (counter.commits, counter.checkouts))
        self.assertEqual(['level-{:03d}'.format(depth) for depth in range(1, RECURSION_DEPTH + 1)], self._names())

    def test_h19_threads_whose_inner_transaction_fails_and_is_swallowed_each_commit_their_own_once(self):
        recording_factory = RecordingConnectionFactory()

        @Transaction()
        def inner():
            with recording_factory.get():
                pass
            raise RuntimeError('inner fails')

        @Transaction()
        def middle():
            try:
                inner()
            except RuntimeError:
                pass
            with recording_factory.get():
                pass

        @Transaction()
        def outer():
            middle()

        errors = []

        def run():
            try:
                outer()
            except BaseException as error:
                errors.append(error)

        workers = [threading.Thread(target=run) for i in range(NESTING_THREADS)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(WAIT_SECONDS)

        self.assertEqual([], errors)
        self.assertEqual(NESTING_THREADS, len(recording_factory.created))
        for connection in recording_factory.created:
            self.assertEqual([NO_ERROR], connection.exit_arguments())   # one commit: nested ones joined it

    def test_h20_a_flush_failure_in_the_second_database_rolls_back_the_first(self):
        first_factory, second_factory = connect_to_mem_db(), connect_to_mem_db()
        for factory in (first_factory, second_factory):
            self.addCleanup(factory.engine.dispose)
        first, second = TransactionWidgetDataAccess(first_factory), TransactionWidgetDataAccess(second_factory)
        second.create(_widget('taken'))

        @Transaction()
        def write_both():
            first.create(_widget('first-database'))
            second.create(_widget('taken'))   # the unique index refuses it at the block's flush

        with self.assertRaises(IntegrityError):
            write_both()

        self.assertEqual([], first.names_in_group(GROUP_ID))
        self.assertEqual(['taken'], second.names_in_group(GROUP_ID))

    def test_h21_a_block_that_commits_the_session_itself_breaks_all_or_nothing(self):
        # Documents the rule (AGENTS.md §5): a DataAccess never commits. One that does saves everything so far at
        # once, and the transaction's rollback can no longer undo it.
        @Transaction()
        def commit_by_hand_then_fail():
            self.transaction_widget_data_access.create(_widget('before-the-hand-commit'))
            with self.factory.get() as session:
                session.commit()
            self.transaction_widget_data_access.create(_widget('after-the-hand-commit'))
            raise RuntimeError('the transaction fails')

        with self.assertRaises(RuntimeError):
            commit_by_hand_then_fail()

        self.assertEqual(['before-the-hand-commit'], self._names())

    def test_h22_a_block_that_rolls_the_session_back_itself_silently_drops_the_earlier_blocks(self):
        # Documents the rule: a DataAccess never rolls back. One that does drops the earlier blocks' writes while the
        # transaction goes on and commits only what comes after.
        @Transaction()
        def roll_back_by_hand():
            self.transaction_widget_data_access.create(_widget('dropped'))
            with self.factory.get() as session:
                session.rollback()
            self.transaction_widget_data_access.create(_widget('kept'))

        roll_back_by_hand()

        self.assertEqual(['kept'], self._names())

    def test_h23_raw_sql_and_bulk_updates_are_part_of_the_transaction(self):
        first_id = self.transaction_widget_data_access.create(_widget('original')).id

        @Transaction()
        def change_with_raw_sql_and_a_bulk_update():
            with self.factory.get() as session:
                session.execute(text('INSERT INTO {} ({}, {}) VALUES (:group_id, :name)'.format(
                    TransactionWidget.__tablename__, TransactionWidget.group_id.key, TransactionWidget.name.key)),
                    {'group_id': GROUP_ID, 'name': 'raw-sql'})
            with self.factory.get() as session:
                session.execute(update(TransactionWidget).where(TransactionWidget.id == first_id)
                                .values(name='bulk-updated'))
            raise RuntimeError('roll back')

        with self.assertRaises(RuntimeError):
            change_with_raw_sql_and_a_bulk_update()

        self.assertEqual(['original'], self._names())

    def test_h24_a_cache_invalidation_called_from_an_after_commit_callback_deletes_at_once(self):
        CoreLib.cache_registry.register(HARD_CASE_CACHE, CacheHandlerRam())
        self.addCleanup(CoreLib.cache_registry.unregister, HARD_CASE_CACHE)
        cache = CoreLib.cache_registry.get(HARD_CASE_CACHE)
        cache.set(CACHE_KEY_VALUE, 'stale', None)

        @Cache(CACHE_KEY_VALUE, handler_name=HARD_CASE_CACHE, invalidate=True)
        def invalidate():
            pass

        @Transaction()
        def write_and_register():
            self.transaction_widget_data_access.create(_widget('main'))
            CoreLib.transaction_scope_registry.get().on_commit.append(invalidate)

        write_and_register()

        self.assertIsNone(cache.get(CACHE_KEY_VALUE))   # the callback runs outside the transaction: no deferral

    def test_h25_after_commit_callbacks_can_chain_transactions_one_after_another(self):
        @Transaction()
        def write_link(number: int):
            self.transaction_widget_data_access.create(_widget('link-{}'.format(number)))
            if number < CALLBACK_CHAIN:
                CoreLib.transaction_scope_registry.get().on_commit.append(lambda: write_link(number + 1))

        write_link(1)

        self.assertEqual(['link-{}'.format(number) for number in range(1, CALLBACK_CHAIN + 1)], self._names())
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_h26_a_factory_with_eq_but_no_hash_fails_loudly_inside_a_transaction(self):
        # Documents the rule: the scope keys connections by the factory, so a transactional factory that defines
        # `__eq__` must define `__hash__` too (Python drops the inherited one). Outside a transaction it works.
        factory = _EqualityWithoutHashFactory()
        with factory.get():
            pass

        @Transaction()
        def use_it():
            with factory.get():
                pass

        with self.assertRaises(TypeError) as raised:
            use_it()

        self.assertIn('unhashable', str(raised.exception))
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_h27_a_recursion_error_inside_a_transaction_rolls_it_back(self):
        def recurse_forever():
            return recurse_forever()

        @Transaction()
        def write_then_recurse():
            self.transaction_widget_data_access.create(_widget('rolled-back'))
            recurse_forever()

        with self.assertRaises(RecursionError):
            write_then_recurse()

        self.assertEqual([], self._names())
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_h28_two_transaction_decorators_on_one_function_are_one_transaction(self):
        @Transaction()
        @Transaction()
        def doubly_decorated():
            self.transaction_widget_data_access.create(_widget('once'))

        with EngineEventCounter(self.factory.engine) as counter:
            doubly_decorated()

        self.assertEqual((1, 1), (counter.commits, counter.checkouts))
        self.assertEqual(['once'], self._names())

    def test_h29_result_to_dict_inside_a_transaction_returns_the_new_rows_id(self):
        @ResultToDict()
        @Transaction()
        def create_as_dict():
            return self.transaction_widget_data_access.create(_widget('as-dict'))

        row = create_as_dict()

        self.assertIsInstance(row[TransactionWidget.id.key], int)
        self.assertEqual('as-dict', row[TransactionWidget.name.key])
