"""@Transaction() with exceptions (the original comes out unchanged, every kind rolls back) and stacked with the
other core-lib decorators in the right order and in the wrong one, each wrong order pinned to what it really does."""
import logging
import sys
import traceback
import unittest
from http import HTTPStatus
from unittest import mock

from sqlalchemy.exc import IntegrityError

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.observer.observer import Observer
from core_lib.observer.observer_decorator import Observe
from core_lib.observer.observer_listener import ObserverListener
from tests.test_data.engine_event_counter import EngineEventCounter
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 81
DECORATOR_TEST_CACHE = 'core_lib_test_transaction_decorator_cache'
CACHE_KEY_NAMES = 'core_lib_test_transaction_decorator_names'
DECORATOR_TEST_OBSERVER = 'core_lib_test_transaction_decorator_observer'
EVENT_WIDGET_WRITTEN = 'EVENT_WIDGET_WRITTEN'
DECORATOR_LOGGER = 'core_lib.connection.transaction_decorator'


def _widget(name: str, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


def _commit_time_duplicate() -> IntegrityError:
    return IntegrityError('INSERT INTO transaction_widget', {}, Exception('UNIQUE constraint failed at commit'))


class _NeedsArguments(Exception):
    """Cannot be built again without its arguments: proves nobody re-creates the exception on the way out."""

    def __init__(self, code: int, detail: str):
        super().__init__(code, detail)
        self.code = code
        self.detail = detail


class _BrokenStr(Exception):
    def __str__(self):
        raise RuntimeError('this exception cannot be printed')


class _StopEverything(BaseException):
    pass


class _RecordingListener(ObserverListener):
    def __init__(self):
        self.events = []

    def update(self, key: str, value):
        self.events.append((key, CoreLib.transaction_scope_registry.get() is not None))


class _no_logs(object):
    """assertNoLogs for Python 3.9 (assertNoLogs is 3.10+): fails if the logger emits anything."""

    def __init__(self, test_case: unittest.TestCase, logger_name: str):
        self.test_case = test_case
        self.logger = logging.getLogger(logger_name)
        self.records = []

    def __enter__(self):
        self.handler = logging.Handler()
        self.handler.emit = self.records.append
        self.logger.addHandler(self.handler)
        return self

    def __exit__(self, exec_type, exec_value, traceback):
        self.logger.removeHandler(self.handler)
        if exec_type is None:
            self.test_case.assertEqual([], [record.getMessage() for record in self.records])
        return False


class TestTransactionDecorator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CoreLib.cache_registry.register(DECORATOR_TEST_CACHE, CacheHandlerRam())

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.unregister(DECORATOR_TEST_CACHE)

    def setUp(self):
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)
        self.cache = CoreLib.cache_registry.get(DECORATOR_TEST_CACHE)
        self.cache.flush_all()

    def _names(self) -> list:
        return self.transaction_widget_data_access.names_in_group(GROUP_ID)

    def _fail_the_commit(self, error: BaseException):
        # inside a transaction: the session's commit at the transaction's end raises `error`
        self.transaction_widget_data_access.current_session().commit = mock.Mock(side_effect=error)

    # exceptions

    def test_x1_the_original_exception_comes_out_unchanged_with_its_traceback(self):
        failure = _NeedsArguments(409, 'the detail')

        def fail_here():
            raise failure

        @Transaction()
        def write_then_fail():
            self.transaction_widget_data_access.create(_widget('rolled-back'))
            fail_here()

        try:   # not assertRaises: it drops the traceback this test reads
            write_then_fail()
            raised = None
        except _NeedsArguments as error:
            raised = error

        self.assertIs(failure, raised)
        self.assertEqual((409, 'the detail'), (raised.code, raised.detail))
        frames = [frame.name for frame in traceback.extract_tb(raised.__traceback__)]
        self.assertEqual(['write_then_fail', 'fail_here'], frames[-2:])   # still ends where it was raised
        self.assertEqual([], self._names())

    def test_x2_a_cause_and_a_context_are_kept_even_when_the_rollback_itself_fails(self):
        cause = KeyError('the cause')
        handled = ValueError('being handled')
        failing_rollback = RecordingConnectionFactory(rollback_error=OSError('the rollback fails'))

        @Transaction()
        def raise_from_a_cause():
            raise LookupError('with a cause') from cause

        @Transaction()
        def raise_while_handling():
            with failing_rollback.get():
                pass
            try:
                raise handled
            except ValueError:
                raise LookupError('while handling')

        with self.assertRaises(LookupError) as with_cause:
            raise_from_a_cause()
        with self.assertLogs('core_lib.connection.transaction_manager', 'ERROR'):
            with self.assertRaises(LookupError) as with_context:
                raise_while_handling()

        self.assertIs(cause, with_cause.exception.__cause__)
        self.assertIs(handled, with_context.exception.__context__)   # the failed rollback did not replace it

    def test_x3_every_kind_of_base_exception_rolls_back_and_goes_up_as_the_same_object(self):
        for failure in (KeyboardInterrupt(), SystemExit(2), GeneratorExit(), _StopEverything(), StopIteration(),
                        MemoryError(), RecursionError()):
            @Transaction()
            def write_then_fail():
                self.transaction_widget_data_access.create(_widget('rolled-back'))
                raise failure

            with self.assertRaises(BaseException) as raised:
                write_then_fail()

            self.assertIs(failure, raised.exception)
            self.assertEqual([], self._names())
            self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_x4_an_exception_that_cannot_be_printed_still_rolls_back(self):
        # the rollback logs the error with its traceback; printing it fails, and logging must not stop the rollback
        failure = _BrokenStr()
        previous = logging.raiseExceptions
        logging.raiseExceptions = False   # logging's own "--- Logging error ---" report, kept off the test output
        self.addCleanup(setattr, logging, 'raiseExceptions', previous)

        @Transaction()
        def write_then_fail():
            self.transaction_widget_data_access.create(_widget('rolled-back'))
            raise failure

        with self.assertRaises(_BrokenStr) as raised:
            write_then_fail()

        self.assertIs(failure, raised.exception)
        self.assertEqual([], self._names())

    def test_x5_a_failed_commit_reaches_the_caller_instead_of_the_return_value(self):
        commit_failure = ConnectionError('the commit fails')
        callbacks_run = []

        @Transaction()
        def write_and_return():
            self.transaction_widget_data_access.create(_widget('never-saved'))
            self._fail_the_commit(commit_failure)
            CoreLib.transaction_scope_registry.get().on_commit.append(lambda: callbacks_run.append('ran'))
            return 'the return value'

        with self.assertRaises(ConnectionError) as raised:
            write_and_return()

        self.assertIs(commit_failure, raised.exception)
        self.assertEqual(([], []), (self._names(), callbacks_run))
        self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_x6_an_error_from_a_nested_transaction_goes_up_unchanged_and_rolls_back_once(self):
        failure = LookupError('the inner transaction fails')

        @Transaction()
        def inner():
            self.transaction_widget_data_access.create(_widget('inner'))
            raise failure

        @Transaction()
        def outer():
            self.transaction_widget_data_access.create(_widget('outer'))
            inner()

        with EngineEventCounter(self.factory.engine) as counter:
            with self.assertRaises(LookupError) as raised:
                outer()

        self.assertIs(failure, raised.exception)
        self.assertEqual((0, 1), (counter.commits, counter.rollbacks))
        self.assertEqual([], self._names())

    def test_x7_decorating_an_async_function_or_a_generator_logs_a_warning_naming_it(self):
        async def an_async_function():
            pass

        async def an_async_generator():
            yield 1

        def a_generator():
            yield 1

        for function in (an_async_function, an_async_generator, a_generator):
            with self.assertLogs(DECORATOR_LOGGER, 'WARNING') as logs:
                Transaction()(function)
            [message] = logs.output
            self.assertIn(function.__qualname__, message)
            self.assertIn('does nothing', message)

    def test_x7_a_plain_function_a_lambda_and_a_method_log_nothing(self):
        class Widgets(object):
            def a_method(self):
                return 'method'

        with _no_logs(self, DECORATOR_LOGGER):
            Transaction()(lambda: 'lambda')
            Transaction()(Widgets.a_method)
            Transaction()(self._names)

    def test_x8_the_warning_comes_once_when_decorating_never_on_each_call(self):
        with self.assertLogs(DECORATOR_LOGGER, 'WARNING') as logs:
            @Transaction()
            def rows():
                yield 1

        with _no_logs(self, DECORATOR_LOGGER):
            for i in range(3):
                list(rows())

        self.assertEqual(1, len(logs.records))

    def test_x9_an_async_function_hidden_behind_another_decorators_plain_wrapper_is_not_seen(self):
        # Documents the limit: the check reads the function it is given; a plain `def` wrapper around an async one
        # looks like a plain function, so no warning comes. Put @Transaction() on the async function itself or not at all.
        def plain_wrapper(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        async def hidden():
            pass

        with _no_logs(self, DECORATOR_LOGGER):
            Transaction()(plain_wrapper(hidden))

    # decorators in the right order and in the wrong one

    def test_d1_duplicate_handler_outside_maps_a_commit_time_duplicate_to_409_inside_it_cannot(self):
        @DuplicateErrorHandler()
        @Transaction()
        def right_order():
            self.transaction_widget_data_access.create(_widget('right'))
            self._fail_the_commit(_commit_time_duplicate())

        @Transaction()
        @DuplicateErrorHandler()
        def wrong_order():
            self.transaction_widget_data_access.create(_widget('wrong'))
            self._fail_the_commit(_commit_time_duplicate())

        with self.assertRaises(StatusCodeException) as right:
            right_order()
        with self.assertRaises(IntegrityError):   # the commit runs outside the handler: no 409
            wrong_order()

        self.assertEqual(HTTPStatus.CONFLICT, right.exception.status_code)
        self.assertEqual([], self._names())

    def test_d1_a_duplicate_found_at_a_blocks_flush_is_409_in_either_order(self):
        self.transaction_widget_data_access.create(_widget('taken'))

        @DuplicateErrorHandler()
        @Transaction()
        def right_order():
            self.transaction_widget_data_access.create(_widget('taken'))

        @Transaction()
        @DuplicateErrorHandler()
        def wrong_order():
            self.transaction_widget_data_access.create(_widget('taken'))

        for duplicate in (right_order, wrong_order):
            with self.assertRaises(StatusCodeException) as raised:
                duplicate()
            self.assertEqual(HTTPStatus.CONFLICT, raised.exception.status_code)
        self.assertEqual(['taken'], self._names())

    def test_d2_a_cached_read_under_the_transaction_decorator_is_never_cached(self):
        reads = []

        @Cache(CACHE_KEY_NAMES, handler_name=DECORATOR_TEST_CACHE)
        @Transaction()
        def right_order():
            reads.append('right')
            return self._names()

        @Transaction()
        @Cache(CACHE_KEY_NAMES, handler_name=DECORATOR_TEST_CACHE)
        def wrong_order():
            reads.append('wrong')
            return self._names()

        self.transaction_widget_data_access.create(_widget('row'))
        right_order(), right_order()
        self.assertEqual(['right'], reads)   # the second call came from the cache, without a transaction
        self.cache.flush_all()
        wrong_order(), wrong_order()

        self.assertEqual(['right', 'wrong', 'wrong'], reads)   # inside a transaction the cache is skipped: every call reads
        self.assertIsNone(self.cache.get(CACHE_KEY_NAMES))

    def test_d3_an_invalidation_waits_for_the_commit_and_is_dropped_on_rollback_in_either_order(self):
        def build(order: str, should_fail: bool):
            def write():
                self.transaction_widget_data_access.create(_widget('{}-{}'.format(order, should_fail)))
                inside['key_still_cached'] = self.cache.get(CACHE_KEY_NAMES) is not None
                if should_fail:
                    raise RuntimeError('roll back')
            invalidating = Cache(CACHE_KEY_NAMES, handler_name=DECORATOR_TEST_CACHE, invalidate=True)
            if order == 'right':
                return invalidating(Transaction()(write))
            return Transaction()(invalidating(write))

        for order in ('right', 'wrong'):
            for should_fail in (False, True):
                inside = {}
                self.cache.set(CACHE_KEY_NAMES, ['stale'], None)
                try:
                    build(order, should_fail)()
                except RuntimeError:
                    pass
                self.assertTrue(inside['key_still_cached'], order)   # never deleted while the transaction is open
                self.assertEqual(should_fail, self.cache.get(CACHE_KEY_NAMES) is not None, (order, should_fail))

    def test_d4_not_found_inside_the_transaction_rolls_the_delete_back_outside_it_commits_first(self):
        @Transaction()
        @NotFoundErrorHandler()
        def not_found_inside(group_id: int):
            self.transaction_widget_data_access.delete_group(GROUP_ID)
            return self.transaction_widget_data_access.names_in_group(group_id)   # empty: 404

        @NotFoundErrorHandler()
        @Transaction()
        def not_found_outside(group_id: int):
            self.transaction_widget_data_access.delete_group(GROUP_ID)
            return self.transaction_widget_data_access.names_in_group(group_id)

        self.transaction_widget_data_access.create(_widget('kept-or-deleted'))
        with self.assertRaises(StatusCodeException):
            not_found_inside(GROUP_ID)
        after_inside = self._names()
        with self.assertRaises(StatusCodeException):
            not_found_outside(GROUP_ID)

        self.assertEqual(['kept-or-deleted'], after_inside)   # the 404 was raised inside: the delete rolled back
        self.assertEqual([], self._names())                   # raised after the commit: the delete is saved

    def test_d5_an_observer_inside_the_transaction_notifies_before_the_commit_outside_it_after(self):
        listener = _RecordingListener()
        CoreLib.observer_registry.register(DECORATOR_TEST_OBSERVER, Observer(listener))
        self.addCleanup(CoreLib.observer_registry.unregister, DECORATOR_TEST_OBSERVER)

        @Observe(event_key=EVENT_WIDGET_WRITTEN, observer_name=DECORATOR_TEST_OBSERVER)
        @Transaction()
        def right_order(name: str, fail_the_commit: bool):
            self.transaction_widget_data_access.create(_widget(name))
            if fail_the_commit:
                self._fail_the_commit(ConnectionError('the commit fails'))

        @Transaction()
        @Observe(event_key=EVENT_WIDGET_WRITTEN, observer_name=DECORATOR_TEST_OBSERVER)
        def wrong_order(name: str, fail_the_commit: bool):
            self.transaction_widget_data_access.create(_widget(name))
            if fail_the_commit:
                self._fail_the_commit(ConnectionError('the commit fails'))

        right_order('right-saved', False)
        with self.assertRaises(ConnectionError):
            right_order('right-lost', True)
        right_events = list(listener.events)
        listener.events.clear()
        wrong_order('wrong-saved', False)
        with self.assertRaises(ConnectionError):
            wrong_order('wrong-lost', True)

        self.assertEqual([(EVENT_WIDGET_WRITTEN, False)], right_events)   # after the commit, and only when it worked
        self.assertEqual([(EVENT_WIDGET_WRITTEN, True)] * 2, listener.events)   # before the commit, even the lost one
        self.assertEqual(['right-saved', 'wrong-saved'], self._names())

    def test_d5_the_right_order_called_inside_another_transaction_notifies_before_the_outer_commit(self):
        # pins today's limit: the inner @Transaction() joins, so @Observe fires when the INNER method returns
        listener = _RecordingListener()
        CoreLib.observer_registry.register(DECORATOR_TEST_OBSERVER, Observer(listener))
        self.addCleanup(CoreLib.observer_registry.unregister, DECORATOR_TEST_OBSERVER)

        @Observe(event_key=EVENT_WIDGET_WRITTEN, observer_name=DECORATOR_TEST_OBSERVER)
        @Transaction()
        def inner(name: str):
            self.transaction_widget_data_access.create(_widget(name))

        @Transaction()
        def outer_that_fails():
            inner('heard-then-lost')
            raise ValueError('the outer transaction fails after the inner one returned')

        with self.assertRaises(ValueError):
            outer_that_fails()

        self.assertEqual([(EVENT_WIDGET_WRITTEN, True)], listener.events)   # heard inside the outer transaction
        self.assertEqual([], self._names())                                 # and the write it heard of was rolled back

    def test_d6_result_to_dict_gives_the_same_row_in_either_order(self):
        @ResultToDict()
        @Transaction()
        def right_order():
            return self.transaction_widget_data_access.create(_widget('right'))

        @Transaction()
        @ResultToDict()
        def wrong_order():
            return self.transaction_widget_data_access.create(_widget('wrong'))

        for create, name in ((right_order, 'right'), (wrong_order, 'wrong')):
            row = create()
            self.assertIsInstance(row[TransactionWidget.id.key], int)
            self.assertEqual((GROUP_ID, name), (row[TransactionWidget.group_id.key], row[TransactionWidget.name.key]))

    def test_d7_transaction_above_staticmethod_or_classmethod_and_below_them(self):
        data_access = self.transaction_widget_data_access

        class Widgets(object):
            @staticmethod
            @Transaction()
            def static_right():
                return data_access.create(_widget('static-right')).id

            @classmethod
            @Transaction()
            def class_right(cls):
                return data_access.create(_widget('class-right')).id

            @Transaction()
            @staticmethod
            def static_wrong():
                return data_access.create(_widget('static-wrong')).id

            @Transaction()
            @classmethod
            def class_wrong(cls):
                return data_access.create(_widget('class-wrong')).id

        Widgets.static_right()
        Widgets.class_right()
        with self.assertRaises(TypeError):   # a classmethod object is not callable: the wrapper cannot call it
            Widgets.class_wrong()
        if sys.version_info < (3, 10):
            with self.assertRaises(TypeError):   # a staticmethod object is callable only from Python 3.10
                Widgets.static_wrong()
        else:
            Widgets.static_wrong()

        expected = ['class-right', 'static-right'] + ([] if sys.version_info < (3, 10) else ['static-wrong'])
        self.assertEqual(sorted(expected), self._names())
        self.assertIsNone(CoreLib.transaction_scope_registry.get())
