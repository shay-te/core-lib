"""@Transaction() with asyncio, every way to run work: to_thread, executors, gather / wait / as_completed /
TaskGroup, semaphores, loop callbacks, run_coroutine_threadsafe, several loops on several threads, cancel and shield,
nested loops. Worker threads run their own transactions; coroutines on the loop's thread join one open there;
cancelling the awaiter never stops a worker's commit; `async def` and generators run outside (the documented limit)."""
import asyncio
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.exc import OperationalError

from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from tests.test_data.recording_connection import EVENT_ENTER, EVENT_EXIT, EVENT_FLUSH, EVENT_RELEASE, NO_ERROR
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 41
OTHER_GROUP_ID = 42
WORKERS = 16
EXECUTOR_THREADS = 4
WAIT_SECONDS = 30
DECORATOR_LOGGER = 'core_lib.connection.transaction_decorator'
MANY_WORKERS = 100
SEMAPHORE_LIMIT = 3
LOOP_THREADS = 4
TRANSACTIONS_PER_LOOP = 25
SMALL_AWAITS = 20


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


class TestTransactionAsyncio(unittest.TestCase):

    def setUp(self):
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)

    def _names(self, group_id: int = GROUP_ID) -> list:
        return self.transaction_widget_data_access.names_in_group(group_id)

    def test_a1_to_thread_workers_each_run_their_own_transaction(self):
        recording_factory = RecordingConnectionFactory()

        @Transaction()
        def one_transaction(number: int):
            with recording_factory.get():
                pass
            with recording_factory.get():
                pass
            return number

        async def main():
            return await asyncio.gather(*[asyncio.to_thread(one_transaction, number) for number in range(WORKERS)])

        self.assertEqual(list(range(WORKERS)), asyncio.run(main()))
        self.assertEqual(WORKERS, len(recording_factory.created))
        for connection in recording_factory.created:
            self.assertEqual(1, len(connection.thread_ids()))
            self.assertEqual([EVENT_ENTER, EVENT_FLUSH, EVENT_RELEASE] * 2 + [EVENT_EXIT], connection.events())
            self.assertEqual([NO_ERROR], connection.exit_arguments())

    def test_a2_executor_threads_and_the_loop_thread_run_transactions_at_once(self):
        recording_factory = RecordingConnectionFactory()

        @Transaction()
        def one_transaction():
            with recording_factory.get():
                pass
            return threading.get_ident()

        async def main():
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor(EXECUTOR_THREADS) as executor:
                in_threads = [loop.run_in_executor(executor, one_transaction) for i in range(WORKERS)]
                on_the_loop = one_transaction()   # the loop's own thread, while the executor works
                return await asyncio.gather(*in_threads), on_the_loop

        thread_ids, loop_thread_id = asyncio.run(main())

        self.assertEqual(threading.get_ident(), loop_thread_id)
        self.assertNotIn(loop_thread_id, thread_ids)
        self.assertEqual(WORKERS + 1, len(recording_factory.created))
        self.assertEqual([[NO_ERROR]] * (WORKERS + 1), [connection.exit_arguments() for connection in recording_factory.created])

    def test_a3_interleaved_tasks_never_carry_a_transaction_across_an_await(self):
        seen_at_awaits = []

        @Transaction()
        def write(name: str):
            self.transaction_widget_data_access.create(_widget(name))

        async def task(prefix: str):
            for i in range(3):
                write('{}-{}'.format(prefix, i))
                seen_at_awaits.append(CoreLib.transaction_scope_registry.get())
                await asyncio.sleep(0)   # lets the other task run between this task's transactions

        async def main():
            await asyncio.gather(task('a'), task('b'))

        asyncio.run(main())

        self.assertEqual([None] * 6, seen_at_awaits)
        self.assertEqual(['a-0', 'a-1', 'a-2', 'b-0', 'b-1', 'b-2'], self._names())

    def test_a4_an_error_in_a_to_thread_transaction_reaches_the_awaiter_and_rolls_back(self):
        failure = LookupError('the worker fails')

        @Transaction()
        def write_then_fail():
            self.transaction_widget_data_access.create(_widget('rolled-back'))
            raise failure

        async def main():
            await asyncio.to_thread(write_then_fail)

        coroutine = main()
        with self.assertRaises(LookupError) as raised:
            asyncio.run(coroutine)

        self.assertIs(failure, raised.exception)
        self.assertEqual([], self._names())

    def test_a5_a_cancelled_or_timed_out_awaiter_does_not_stop_the_workers_commit(self):
        release_worker = threading.Event()
        worker_done = threading.Event()

        @Transaction()
        def slow_write(name: str):
            release_worker.wait(WAIT_SECONDS)
            self.transaction_widget_data_access.create(_widget(name))
            worker_done.set()

        async def time_out():
            await asyncio.wait_for(asyncio.to_thread(slow_write, 'after-the-timeout'), timeout=0.05)

        async def main():
            with self.assertRaises(asyncio.TimeoutError):
                await time_out()
            release_worker.set()   # the thread cannot be cancelled: it goes on and commits
            await asyncio.to_thread(worker_done.wait, WAIT_SECONDS)

        asyncio.run(main())

        self.assertEqual(['after-the-timeout'], self._names())

    def test_a6_a_nested_event_loop_inside_a_transaction_joins_it_on_the_same_thread_but_not_from_a_worker(self):
        # asyncio.run inside a transaction runs its coroutines on the transaction's own thread, so their writes join
        # the transaction (and roll back with it); a write sent to a worker thread commits on its own.
        other_data_access = TransactionWidgetDataAccess(connect_to_file_db(self))   # its own database: see a8

        async def write_on_the_loop_and_in_a_worker():
            self.transaction_widget_data_access.create(_widget('on-the-loop'))
            await asyncio.to_thread(other_data_access.create, _widget('in-a-worker'))

        @Transaction()
        def run_a_loop_then_fail():
            asyncio.run(write_on_the_loop_and_in_a_worker())
            raise RuntimeError('the transaction fails')

        with self.assertRaises(RuntimeError):
            run_a_loop_then_fail()

        self.assertEqual([], self._names())                                       # rolled back with the transaction
        self.assertEqual(['in-a-worker'], other_data_access.names_in_group(GROUP_ID))   # committed on its own

    def test_a7_an_async_function_runs_after_its_transaction_ended_so_its_error_rolls_nothing_back(self):
        # Documents the limit: decorate a plain `def`. Calling an `async def` only builds the coroutine, so the
        # transaction begins and ends empty; the body runs later, outside it, and each write commits on its own.
        with self.assertLogs(DECORATOR_LOGGER, 'WARNING'):   # the decorator warns about it when applied
            @Transaction()
            async def write_then_fail():
                self.transaction_widget_data_access.create(_widget('async-write'))
                raise RuntimeError('fails after the write')

        coroutine = write_then_fail()
        self.assertIsNone(CoreLib.transaction_scope_registry.get())
        with self.assertRaises(RuntimeError):
            asyncio.run(coroutine)

        self.assertEqual(['async-write'], self._names())


    def test_a8_waiting_inside_a_transaction_for_a_worker_that_writes_the_same_database_deadlocks(self):
        # Documents the limit: the transaction holds the database's write lock until it ends, so a worker it waits
        # for cannot write there. sqlite gives up after its 5-second busy timeout; another database may wait forever.
        @Transaction()
        def write_then_wait_for_a_worker():
            self.transaction_widget_data_access.create(_widget('holds-the-lock'))
            with ThreadPoolExecutor(1) as executor:
                return executor.submit(self.transaction_widget_data_access.create, _widget('waits')).result()

        with self.assertRaises(OperationalError) as raised:
            write_then_wait_for_a_worker()

        self.assertIn('database is locked', str(raised.exception))
        self.assertEqual([], self._names())   # the worker's error went up through the transaction: rolled back

    def _write_or_fail(self, name: str, should_fail: bool, group_id: int = GROUP_ID):
        @Transaction()
        def write():
            self.transaction_widget_data_access.create(_widget(name, group_id))
            if should_fail:
                raise LookupError('{} fails'.format(name))
        write()
        return name

    def test_a9_the_default_executor_runs_each_transaction_on_its_own(self):
        async def main():
            loop = asyncio.get_running_loop()
            calls = [loop.run_in_executor(None, self._write_or_fail, 'e{}'.format(i), i == 1) for i in range(3)]
            return await asyncio.gather(*calls, return_exceptions=True)

        results = asyncio.run(main())

        self.assertEqual(['e0', 'e2'], [result for result in results if isinstance(result, str)])
        self.assertIsInstance(results[1], LookupError)
        self.assertEqual(['e0', 'e2'], self._names())

    def test_a10_gather_with_return_exceptions_keeps_only_the_transactions_that_committed(self):
        async def main():
            return await asyncio.gather(*[asyncio.to_thread(self._write_or_fail, 'g{:02d}'.format(i), i % 3 == 0)
                                          for i in range(9)], return_exceptions=True)

        results = asyncio.run(main())

        committed = ['g{:02d}'.format(i) for i in range(9) if i % 3 != 0]
        self.assertEqual(committed, [result for result in results if isinstance(result, str)])
        self.assertEqual(3, len([result for result in results if isinstance(result, LookupError)]))
        self.assertEqual(committed, self._names())

    def test_a11_wait_first_exception_and_as_completed_let_every_started_transaction_finish(self):
        async def main():
            tasks = [asyncio.ensure_future(asyncio.to_thread(self._write_or_fail, 'w{}'.format(i), i == 0))
                     for i in range(4)]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            finished = [await task for task in asyncio.as_completed(pending)]   # the rest still run to the end
            return done, finished

        done, finished = asyncio.run(main())

        self.assertTrue(any(isinstance(task.exception(), LookupError) for task in done))
        self.assertEqual(['w1', 'w2', 'w3'], self._names())
        self.assertEqual(3, len([task for task in done if task.exception() is None]) + len(finished))

    def test_a12_more_to_thread_transactions_than_the_default_executor_has_threads(self):
        recording_factory = RecordingConnectionFactory()

        @Transaction()
        def one_transaction():
            with recording_factory.get():
                pass

        async def main():
            await asyncio.gather(*[asyncio.to_thread(one_transaction) for i in range(MANY_WORKERS)])

        asyncio.run(main())

        self.assertEqual(MANY_WORKERS, len(recording_factory.created))
        self.assertEqual([[NO_ERROR]] * MANY_WORKERS, [connection.exit_arguments() for connection in recording_factory.created])

    def test_a13_a_semaphore_bounds_how_many_transactions_are_open_at_once(self):
        recording_factory = RecordingConnectionFactory()
        open_now = []
        most_open = []
        lock = threading.Lock()

        @Transaction()
        def one_transaction():
            with recording_factory.get():
                with lock:
                    open_now.append(1)
                    most_open.append(len(open_now))
                time.sleep(0.005)
                with lock:
                    open_now.pop()

        async def main():
            semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

            async def bounded():
                async with semaphore:
                    await asyncio.to_thread(one_transaction)

            await asyncio.gather(*[bounded() for i in range(WORKERS)])

        asyncio.run(main())

        self.assertLessEqual(max(most_open), SEMAPHORE_LIMIT)
        self.assertEqual(WORKERS, len(recording_factory.created))

    def test_a14_loop_callbacks_scheduled_inside_a_transaction_run_after_it_outside_it(self):
        seen = []

        def callback(name: str):
            seen.append((name, CoreLib.transaction_scope_registry.get()))

        @Transaction()
        def schedule(loop):
            self.transaction_widget_data_access.create(_widget('scheduler'))
            loop.call_soon(callback, 'call_soon')
            loop.call_later(0.01, callback, 'call_later')
            seen.append(('inside', CoreLib.transaction_scope_registry.get() is not None))

        async def main():
            schedule(asyncio.get_running_loop())   # a sync transaction blocks the loop: nothing runs meanwhile
            await asyncio.sleep(0.05)

        asyncio.run(main())

        self.assertEqual([('inside', True), ('call_soon', None), ('call_later', None)], seen)
        self.assertEqual(['scheduler'], self._names())

    def test_a15_a_coroutine_sent_from_a_worker_transaction_to_the_loop_runs_outside_it(self):
        recording_factory = RecordingConnectionFactory()
        seen = {}

        async def on_the_loop():
            seen['loop_thread_scope'] = CoreLib.transaction_scope_registry.get()
            return threading.get_ident()

        def worker(loop):
            @Transaction()
            def in_a_transaction():
                with recording_factory.get():
                    pass
                seen['worker_scope'] = CoreLib.transaction_scope_registry.get()
                return asyncio.run_coroutine_threadsafe(on_the_loop(), loop).result(WAIT_SECONDS)
            return in_a_transaction()

        async def main():
            return await asyncio.to_thread(worker, asyncio.get_running_loop()), threading.get_ident()

        coroutine_thread, loop_thread = asyncio.run(main())

        self.assertEqual(loop_thread, coroutine_thread)
        self.assertIsNotNone(seen['worker_scope'])
        self.assertIsNone(seen['loop_thread_scope'])
        self.assertEqual([[NO_ERROR]], [connection.exit_arguments() for connection in recording_factory.created])

    def test_a16_several_event_loops_on_several_threads_keep_their_transactions_apart(self):
        recording_factory = RecordingConnectionFactory()
        errors = []

        @Transaction()
        def one_transaction(should_fail: bool):
            with recording_factory.get():
                pass
            if should_fail:
                raise LookupError('fails')

        async def loop_body(index: int):
            for i in range(TRANSACTIONS_PER_LOOP):
                try:
                    one_transaction((index + i) % 4 == 0)
                except LookupError:
                    pass
                await asyncio.sleep(0)

        def run_a_loop(index: int):
            try:
                asyncio.run(loop_body(index))
            except BaseException as error:
                errors.append(error)

        threads = [threading.Thread(target=run_a_loop, args=(index,)) for index in range(LOOP_THREADS)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(WAIT_SECONDS)

        self.assertEqual([], errors)
        self.assertEqual(LOOP_THREADS * TRANSACTIONS_PER_LOOP, len(recording_factory.created))
        for connection in recording_factory.created:
            self.assertEqual(1, len(connection.thread_ids()))
            self.assertEqual(1, len(connection.exit_arguments()))

    def test_a17_cancelling_a_gather_of_worker_transactions_lets_every_worker_commit(self):
        release = threading.Event()

        @Transaction()
        def slow_write(name: str):
            release.wait(WAIT_SECONDS)
            self.transaction_widget_data_access.create(_widget(name))

        async def main():
            gathered = asyncio.gather(*[asyncio.to_thread(slow_write, 'c{}'.format(i)) for i in range(3)])
            await asyncio.sleep(0.05)
            gathered.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await gathered
            release.set()   # the threads were never stopped: they go on and commit
            loop = asyncio.get_running_loop()
            await loop.shutdown_default_executor()

        asyncio.run(main())

        self.assertEqual(['c0', 'c1', 'c2'], self._names())

    def test_a18_a_shielded_worker_transaction_commits_when_its_awaiter_is_cancelled(self):
        @Transaction()
        def write():
            time.sleep(0.05)
            self.transaction_widget_data_access.create(_widget('shielded'))

        async def main():
            inner = asyncio.ensure_future(asyncio.to_thread(write))
            outer = asyncio.ensure_future(asyncio.shield(inner))
            await asyncio.sleep(0.01)
            outer.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await outer
            await inner   # the shielded work goes on to its commit

        asyncio.run(main())

        self.assertEqual(['shielded'], self._names())

    def test_a19_an_async_generator_and_a_generator_run_after_their_transaction_ended(self):
        # Documents the limit: like an `async def`, calling a generator only builds it; the body runs later, outside.
        with self.assertLogs(DECORATOR_LOGGER, 'WARNING') as logs:   # the decorator warns about each when applied
            @Transaction()
            async def async_rows():
                self.transaction_widget_data_access.create(_widget('async-generator'))
                yield CoreLib.transaction_scope_registry.get()
                raise RuntimeError('fails after the write')

            @Transaction()
            def rows():
                self.transaction_widget_data_access.create(_widget('generator'))
                yield CoreLib.transaction_scope_registry.get()
        self.assertEqual(2, len(logs.records))

        async def consume():
            return [scope async for scope in async_rows()]

        coroutine = consume()
        with self.assertRaises(RuntimeError):
            asyncio.run(coroutine)
        scopes = list(rows())

        self.assertEqual([None], scopes)   # no transaction around the body
        self.assertEqual(['async-generator', 'generator'], self._names())   # each write committed on its own

    @unittest.skipUnless(hasattr(asyncio, 'TaskGroup'), 'asyncio.TaskGroup is Python 3.11+')
    def test_a20_a_task_group_whose_task_fails_leaves_the_other_workers_committed(self):
        async def main():
            async with asyncio.TaskGroup() as group:
                group.create_task(asyncio.to_thread(self._write_or_fail, 'kept', False))
                group.create_task(asyncio.to_thread(self._write_or_fail, 'rolled-back', True))

        coroutine = main()
        with self.assertRaises(BaseException):   # an ExceptionGroup
            asyncio.run(coroutine)

        self.assertEqual(['kept'], self._names())

    def test_a21_a_loop_run_on_a_worker_thread_inside_a_transaction_commits_on_its_own(self):
        other_data_access = TransactionWidgetDataAccess(connect_to_file_db(self))   # its own database: see a8

        async def write_on_the_worker_loop():
            other_data_access.create(_widget('worker-loop'))
            return CoreLib.transaction_scope_registry.get()

        @Transaction()
        def run_a_loop_in_a_worker_then_fail():
            self.transaction_widget_data_access.create(_widget('parent'))
            with ThreadPoolExecutor(1) as executor:
                worker_scope = executor.submit(asyncio.run, write_on_the_worker_loop()).result(WAIT_SECONDS)
            self.assertIsNone(worker_scope)
            raise RuntimeError('the parent fails')

        with self.assertRaises(RuntimeError):
            run_a_loop_in_a_worker_then_fail()

        self.assertEqual([], self._names())
        self.assertEqual(['worker-loop'], other_data_access.names_in_group(GROUP_ID))

    def test_a22_many_small_awaited_functions_inside_one_transaction_all_join_it_and_roll_back_together(self):
        # A sync @Transaction() method may run async code with asyncio.run: every coroutine runs on the transaction's
        # own thread, so each small await's write joins the one transaction, gathered or one after the other.
        async def write_one(name: str):
            await asyncio.sleep(0)   # gives the other coroutines a turn, on the same thread
            self.transaction_widget_data_access.create(_widget(name))
            return CoreLib.transaction_scope_registry.get()

        async def many_small_awaits():
            in_a_row = [await write_one('row-{:02d}'.format(i)) for i in range(SMALL_AWAITS // 2)]
            gathered = await asyncio.gather(*[write_one('gathered-{:02d}'.format(i)) for i in range(SMALL_AWAITS // 2)])
            return in_a_row + list(gathered)

        @Transaction()
        def run_the_awaits(should_fail: bool):
            scopes = asyncio.run(many_small_awaits())
            if should_fail:
                raise RuntimeError('the transaction fails after all the awaits')
            return scopes, CoreLib.transaction_scope_registry.get()

        with self.assertRaises(RuntimeError):
            run_the_awaits(True)
        after_failure = self._names()
        scopes, transaction_scope = run_the_awaits(False)

        self.assertEqual([], after_failure)                                  # all twenty rolled back together
        self.assertEqual([transaction_scope] * SMALL_AWAITS, scopes)         # every await was inside the one transaction
        self.assertEqual(SMALL_AWAITS, len(self._names()))
