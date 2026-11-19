"""@Transaction() on SQLAlchemy: every DataAccess call shares one session, each block only flushes,
and the session commits once when the function returns or rolls back when it raises."""
import unittest
from http import HTTPStatus
from unittest import mock

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.connection.sql_alchemy_connection import SqlAlchemyConnection
from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
from core_lib.error_handling.status_code_exception import StatusCodeException
from tests.test_data.engine_event_counter import EngineEventCounter
from tests.test_data.test_utils import connect_to_file_db, connect_to_mem_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess
from tests.test_data.transaction_widget_service import TRANSACTION_TEST_CACHE, TransactionWidgetService

GROUP_ID = 3
FLOW_GROUP_ID = 7
ABSENT_WIDGET_ID = 2_000_000_000
SQL_ALCHEMY_CONNECTION_LOGGER = 'core_lib.connection.sql_alchemy_connection'


class _Abort(BaseException):
    pass


def _widget(name, group_id: int = GROUP_ID) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


class TestTransactionSqlAlchemy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CoreLib.cache_registry.register(TRANSACTION_TEST_CACHE, CacheHandlerRam())

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.unregister(TRANSACTION_TEST_CACHE)

    def setUp(self):
        self.factory = connect_to_mem_db()
        self.addCleanup(self.factory.engine.dispose)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)
        CoreLib.cache_registry.get(TRANSACTION_TEST_CACHE).flush_all()

    def _use_file_db(self):
        # Pool checkout / checkin events do not fire on the in-memory pool; a sqlite file fires them.
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)

    def test_s1_two_creates_commit_once_at_the_end(self):
        commits_seen_inside = []

        @Transaction()
        def create_two():
            self.transaction_widget_data_access.create(_widget('acme'))
            commits_seen_inside.append(counter.commits)
            self.transaction_widget_data_access.create(_widget('beta'))
            commits_seen_inside.append(counter.commits)

        with EngineEventCounter(self.factory.engine) as counter:
            create_two()

        self.assertEqual([0, 0], commits_seen_inside)
        self.assertEqual(1, counter.commits)
        self.assertEqual(['acme', 'beta'], self.transaction_widget_data_access.names_in_group(GROUP_ID))

    def test_s2_an_error_rolls_back_and_propagates_unchanged(self):
        failure = RuntimeError('after the create')

        @Transaction()
        def create_then_fail():
            self.transaction_widget_data_access.create(_widget('acme'))
            raise failure

        with EngineEventCounter(self.factory.engine) as counter:
            with self.assertLogs(SQL_ALCHEMY_CONNECTION_LOGGER, 'ERROR') as logs:
                with self.assertRaises(RuntimeError) as raised:
                    create_then_fail()

        self.assertIs(failure, raised.exception)
        self.assertEqual(0, counter.commits)
        self.assertGreaterEqual(counter.rollbacks, 1)
        self.assertIs(failure, logs.records[0].exc_info[1])
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

    def test_s3_create_returns_the_id_before_the_function_returns(self):
        ids_inside = []

        @Transaction()
        def create_one():
            widget = self.transaction_widget_data_access.create(_widget('acme'))
            ids_inside.append(widget.id)
            return widget.id

        widget_id = create_one()

        self.assertIsInstance(ids_inside[0], int)
        self.assertEqual(ids_inside[0], widget_id)
        self.assertEqual('acme', self.transaction_widget_data_access.get(widget_id).name)

    def test_s4_a_duplicate_raises_at_the_data_access_call_and_undoes_the_first_row(self):
        steps = []

        @Transaction()
        def create_duplicate():
            self.transaction_widget_data_access.create(_widget('acme'))
            steps.append('first create returned')
            try:
                self.transaction_widget_data_access.create(_widget('acme'))
            except IntegrityError:
                steps.append('second create raised')
                raise
            steps.append('second create returned')

        with self.assertRaises(IntegrityError):
            create_duplicate()

        self.assertEqual(['first create returned', 'second create raised'], steps)
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

    def test_s4_under_duplicate_error_handler_the_duplicate_is_a_conflict(self):
        @DuplicateErrorHandler()
        @Transaction()
        def create_duplicate():
            self.transaction_widget_data_access.create(_widget('acme'))
            self.transaction_widget_data_access.create(_widget('acme'))

        with self.assertRaises(StatusCodeException) as raised:
            create_duplicate()

        self.assertEqual(HTTPStatus.CONFLICT, raised.exception.status_code)
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

    def test_s5_a_null_column_raises_at_the_call_and_commits_nothing(self):
        steps = []

        @Transaction()
        def create_nameless():
            self.transaction_widget_data_access.create(_widget('acme'))
            try:
                self.transaction_widget_data_access.create(_widget(None))
            except IntegrityError:
                steps.append('create raised')
                raise

        with EngineEventCounter(self.factory.engine) as counter:
            with self.assertRaises(IntegrityError):
                create_nameless()

        self.assertEqual(['create raised'], steps)
        self.assertEqual(0, counter.commits)
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

    def test_s6_a_nested_transaction_joins_and_an_outer_failure_undoes_the_inner_write(self):
        sessions = {}
        commits_after_inner = []

        @Transaction()
        def inner():
            sessions['inner'] = self.transaction_widget_data_access.current_session()
            self.transaction_widget_data_access.create(_widget('acme'))

        @Transaction()
        def outer():
            sessions['outer'] = self.transaction_widget_data_access.current_session()
            inner()
            commits_after_inner.append(counter.commits)
            raise RuntimeError('outer failed')

        with EngineEventCounter(self.factory.engine) as counter:
            with self.assertRaises(RuntimeError):
                outer()

        self.assertIs(sessions['outer'], sessions['inner'])
        self.assertEqual([0], commits_after_inner)
        self.assertEqual(0, counter.commits)
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

    def test_s7_a_recursive_transaction_commits_once(self):
        @Transaction()
        def create_level(level: int):
            self.transaction_widget_data_access.create(_widget('level-{}'.format(level)))
            if level < 3:
                create_level(level + 1)

        with EngineEventCounter(self.factory.engine) as counter:
            create_level(1)

        self.assertEqual(1, counter.commits)
        self.assertEqual(['level-1', 'level-2', 'level-3'],
                         self.transaction_widget_data_access.names_in_group(GROUP_ID))

    def test_s8_without_a_transaction_each_block_commits_on_its_own(self):
        with EngineEventCounter(self.factory.engine) as counter:
            self.transaction_widget_data_access.create(_widget('acme'))
            duplicate = _widget('acme')
            with self.assertRaises(IntegrityError):
                self.transaction_widget_data_access.create(duplicate)

        self.assertEqual(1, counter.commits)
        self.assertEqual(['acme'], self.transaction_widget_data_access.names_in_group(GROUP_ID))
        first_session = self.transaction_widget_data_access.current_session()
        second_session = self.transaction_widget_data_access.current_session()
        self.assertIsNot(first_session, second_session)

    def test_s9_a_swallowed_not_found_does_not_hurt_the_transaction(self):
        statuses = []

        @Transaction()
        def create_look_up_create():
            self.transaction_widget_data_access.create(_widget('acme'))
            try:
                self.transaction_widget_data_access.get(ABSENT_WIDGET_ID)
            except StatusCodeException as missing:
                statuses.append(missing.status_code)
            self.transaction_widget_data_access.create(_widget('beta'))

        create_look_up_create()

        self.assertEqual([HTTPStatus.NOT_FOUND], statuses)
        self.assertEqual(['acme', 'beta'], self.transaction_widget_data_access.names_in_group(GROUP_ID))

    def test_s10_a_swallowed_database_error_fails_the_commit_and_still_releases_the_connection(self):
        self._use_file_db()

        @Transaction()
        def swallow_duplicate():
            self.transaction_widget_data_access.create(_widget('acme'))
            try:
                self.transaction_widget_data_access.create(_widget('acme'))
            except IntegrityError:
                pass

        caught = None
        with EngineEventCounter(self.factory.engine) as counter:
            try:
                swallow_duplicate()
            except PendingRollbackError as error:
                caught = error
            # counted while `caught` still holds the frames, so garbage collection cannot return a leak
            checkouts, checkins = counter.checkouts, counter.checkins

        self.assertIsInstance(caught, PendingRollbackError)
        self.assertEqual(1, checkouts)
        self.assertEqual(checkouts, checkins)
        self.assertEqual(0, counter.commits)
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

    def test_s11_a_swallowed_error_that_is_not_from_the_database_lets_it_commit(self):
        @Transaction()
        def swallow_value_error():
            self.transaction_widget_data_access.create(_widget('acme'))
            try:
                self.transaction_widget_data_access.raise_inside_block('not a database error')
            except ValueError:
                pass

        swallow_value_error()

        self.assertEqual(['acme'], self.transaction_widget_data_access.names_in_group(GROUP_ID))

    def test_s12_rows_returned_from_a_transaction_are_readable_after_the_commit(self):
        @Transaction()
        def create_entity():
            return self.transaction_widget_data_access.create(_widget('acme'))

        @ResultToDict()
        @Transaction()
        def create_dict():
            return self.transaction_widget_data_access.create(_widget('beta'))

        entity = create_entity()
        row = create_dict()

        self.assertTrue(inspect(entity).detached)
        self.assertIsInstance(entity.id, int)
        self.assertEqual('acme', entity.name)
        self.assertEqual('beta', row[TransactionWidget.name.key])
        self.assertEqual(GROUP_ID, row[TransactionWidget.group_id.key])
        self.assertEqual(entity.id + 1, row[TransactionWidget.id.key])

    def test_s13_a_transaction_that_asks_for_no_connection_checks_out_nothing(self):
        self._use_file_db()

        @Transaction()
        def answer():
            return 42

        with EngineEventCounter(self.factory.engine) as counter:
            result = answer()

        self.assertEqual(42, result)
        self.assertEqual(0, counter.checkouts)
        self.assertEqual(0, counter.commits)

    def test_s14_a_base_exception_rolls_back_too(self):
        abort = _Abort()

        @Transaction()
        def create_then_abort():
            self.transaction_widget_data_access.create(_widget('acme'))
            raise abort

        with EngineEventCounter(self.factory.engine) as counter:
            with self.assertRaises(_Abort) as raised:
                create_then_abort()

        self.assertIs(abort, raised.exception)
        self.assertEqual(0, counter.commits)
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

    def test_s15_five_data_access_calls_check_out_one_connection(self):
        self._use_file_db()

        def five_calls():
            self.transaction_widget_data_access.create(_widget('acme'))
            self.transaction_widget_data_access.create(_widget('beta'))
            self.transaction_widget_data_access.names_in_group(GROUP_ID)
            self.transaction_widget_data_access.count_all()
            self.transaction_widget_data_access.delete_group(GROUP_ID + 1)

        with EngineEventCounter(self.factory.engine) as inside:
            Transaction()(five_calls)()
        self.transaction_widget_data_access.delete_group(GROUP_ID)
        with EngineEventCounter(self.factory.engine) as outside:
            five_calls()

        self.assertEqual((1, 1, 1), (inside.checkouts, inside.checkins, inside.commits))
        self.assertEqual(5, outside.checkouts)

    def test_s16_one_session_per_transaction_and_a_new_one_per_block_outside(self):
        @Transaction()
        def two_sessions():
            return (self.transaction_widget_data_access.current_session(),
                    self.transaction_widget_data_access.current_session())

        first_a, first_b = two_sessions()
        second_a, second_b = two_sessions()
        outside = [self.transaction_widget_data_access.current_session() for i in range(3)]

        self.assertIs(first_a, first_b)
        self.assertIs(second_a, second_b)
        self.assertIsNot(first_a, second_a)
        self.assertEqual(3, len({id(session) for session in outside}))
        self.assertNotIn(first_a, outside)

    def test_s17_the_session_is_ended_once_by_the_transaction_never_by_a_block(self):
        original_exit = SqlAlchemyConnection.__exit__
        original_end = SqlAlchemyConnection.end
        original_close = SqlAlchemyConnection.close

        @Transaction()
        def three_calls(name: str, fail_in_a_fourth: bool):
            self.transaction_widget_data_access.create(_widget(name))
            self.transaction_widget_data_access.names_in_group(GROUP_ID)
            self.transaction_widget_data_access.count_all()
            if fail_in_a_fourth:
                self.transaction_widget_data_access.raise_inside_block('fourth call fails')

        def counts(connection_exit, connection_end, connection_close):
            return (connection_exit.call_count, connection_end.call_count, connection_close.call_count,
                    connection_end.call_args[0][1:])

        with mock.patch.object(SqlAlchemyConnection, '__exit__', autospec=True,
                               side_effect=original_exit) as connection_exit, \
                mock.patch.object(SqlAlchemyConnection, 'end', autospec=True,
                                  side_effect=original_end) as connection_end, \
                mock.patch.object(SqlAlchemyConnection, 'close', autospec=True,
                                  side_effect=original_close) as connection_close:
            three_calls('acme', False)
            success = counts(connection_exit, connection_end, connection_close)
            for patched in (connection_exit, connection_end, connection_close):
                patched.reset_mock()
            with self.assertRaises(ValueError):
                three_calls('beta', True)
            failure = counts(connection_exit, connection_end, connection_close)

        # every block exits (3, then 4 with the failing one) without ending the session; the transaction ends it
        # once (`end`), and only that end closes it
        self.assertEqual((3, 1, 1, (None, None, None)), success)
        exit_calls, end_calls, close_calls, (exec_type, exec_value, traceback) = failure
        self.assertEqual((4, 1, 1), (exit_calls, end_calls, close_calls))
        self.assertIs(ValueError, exec_type)
        self.assertEqual('fourth call fails', str(exec_value))
        self.assertIsNotNone(traceback)

    def test_s19_flow_replace_group_is_all_or_nothing(self):
        transaction_widget_service = TransactionWidgetService(self.transaction_widget_data_access)

        self.assertEqual(['acme', 'beta'], transaction_widget_service.replace_group(FLOW_GROUP_ID, ['acme', 'beta']))
        with self.assertRaises(StatusCodeException) as raised:
            transaction_widget_service.replace_group(FLOW_GROUP_ID, ['gamma', 'gamma'])
        self.assertEqual(HTTPStatus.CONFLICT, raised.exception.status_code)
        self.assertEqual(['acme', 'beta'], transaction_widget_service.list_group(FLOW_GROUP_ID))
        self.assertEqual(['acme', 'beta'], self.transaction_widget_data_access.names_in_group(FLOW_GROUP_ID))

        self.assertEqual(['delta'], transaction_widget_service.replace_group(FLOW_GROUP_ID, ['delta']))
        self.assertEqual(['delta'], self.transaction_widget_data_access.names_in_group(FLOW_GROUP_ID))

    def test_s20_a_read_inside_the_transaction_sees_its_own_uncommitted_rows(self):
        commits_at_read = []

        @Transaction()
        def create_two_then_read():
            self.transaction_widget_data_access.create(_widget('acme'))
            self.transaction_widget_data_access.create(_widget('beta'))
            commits_at_read.append(counter.commits)
            return self.transaction_widget_data_access.names_in_group(GROUP_ID)

        with EngineEventCounter(self.factory.engine) as counter:
            names = create_two_then_read()

        self.assertEqual(['acme', 'beta'], names)
        self.assertEqual([0], commits_at_read)

    def test_s21_outside_a_transaction_a_failed_commit_still_releases_the_connection(self):
        self._use_file_db()
        self.transaction_widget_data_access.create(_widget('acme'))
        reached_end_of_block = []

        def add_a_duplicate():
            with self.factory.get() as session:
                session.add(TransactionWidget(**_widget('acme')))
                reached_end_of_block.append(True)

        with EngineEventCounter(self.factory.engine) as counter:
            with self.assertRaises(IntegrityError):
                add_a_duplicate()

        self.assertEqual([True], reached_end_of_block)
        self.assertEqual(1, counter.checkouts)
        self.assertEqual(counter.checkouts, counter.checkins)
        self.assertEqual(['acme'], self.transaction_widget_data_access.names_in_group(GROUP_ID))
