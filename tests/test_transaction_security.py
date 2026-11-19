"""@Transaction() and security: one request never sees, reaches or ends another's transaction; a killed request
saves nothing; a check-then-write needs the database to refuse; a failed write never logs the values it wrote."""
import logging
import threading
import unittest
from http import HTTPStatus

from omegaconf import OmegaConf
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.connection.transaction_decorator import Transaction
from core_lib.connection.transaction_scope import TransactionScope
from core_lib.core_lib import CoreLib
from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
from core_lib.error_handling.status_code_exception import StatusCodeException
from tests.test_data.test_utils import connect_to_file_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

SECRET_GROUP_ID = 21
SLOT_GROUP_ID = 22
WAIT_SECONDS = 30
READER_COUNT = 5
READS_PER_READER = 20
SECRET_VALUE = 'secret-value-7f3a'
CONNECTION_LOGGER = 'core_lib.connection.sql_alchemy_connection'
SQLALCHEMY_ENGINE_LOGGER = 'sqlalchemy.engine'


def _widget(name: str, group_id: int) -> dict:
    return {TransactionWidget.group_id.key: group_id, TransactionWidget.name.key: name}


class _KeepRecords(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.messages = []

    def emit(self, record):
        self.messages.append(self.format(record))


class TestTransactionSecurity(unittest.TestCase):

    def setUp(self):
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)

    def _names(self, group_id: int) -> list:
        return self.transaction_widget_data_access.names_in_group(group_id)

    def _run_in_threads(self, targets: list) -> list:
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

    def test_sec1_concurrent_readers_never_see_another_requests_uncommitted_or_rolled_back_rows(self):
        written = threading.Event()
        readers_done = threading.Barrier(READER_COUNT + 1, timeout=WAIT_SECONDS)
        leaked = []

        @Transaction()
        def write_then_roll_back():
            for i in range(3):
                self.transaction_widget_data_access.create(_widget('uncommitted-{}'.format(i), SECRET_GROUP_ID))
            written.set()
            readers_done.wait()   # every reader has looked while these rows were written but not committed
            raise RuntimeError('the request fails')

        @Transaction()
        def read_in_a_transaction():
            return self._names(SECRET_GROUP_ID)

        def read():
            written.wait(WAIT_SECONDS)
            for i in range(READS_PER_READER):
                leaked.extend(read_in_a_transaction())
                leaked.extend(self._names(SECRET_GROUP_ID))
            readers_done.wait()

        errors = self._run_in_threads([write_then_roll_back] + [read] * READER_COUNT)

        self.assertEqual(['the request fails'], [str(error) for error in errors])
        self.assertEqual([], leaked)
        self.assertEqual([], self._names(SECRET_GROUP_ID))

    def test_sec2_a_killed_request_saves_nothing_and_its_interrupt_goes_up_unchanged(self):
        for interrupt in (KeyboardInterrupt(), SystemExit(3)):
            @Transaction()
            def killed_half_way():
                self.transaction_widget_data_access.create(_widget('half-done', SECRET_GROUP_ID))
                raise interrupt

            with self.assertRaises(BaseException) as raised:
                killed_half_way()

            self.assertIs(interrupt, raised.exception)
            self.assertEqual([], self._names(SECRET_GROUP_ID))
            self.assertIsNone(CoreLib.transaction_scope_registry.get())

    def test_sec3_another_thread_cannot_reach_end_or_replace_this_threads_transaction(self):
        other_thread_saw = {}
        own = {}

        def other_thread():
            other_thread_saw['scope'] = CoreLib.transaction_scope_registry.get()
            other_thread_saw['session'] = self.transaction_widget_data_access.current_session()
            with self.assertRaises(KeyError):
                CoreLib.transaction_scope_registry.unregister()        # it has no transaction of its own to end
            CoreLib.transaction_scope_registry.register(TransactionScope())   # registering touches only its own entry
            other_thread_saw['own_scope'] = CoreLib.transaction_scope_registry.get()
            CoreLib.transaction_scope_registry.unregister()

        @Transaction()
        def request():
            self.transaction_widget_data_access.create(_widget('mine', SECRET_GROUP_ID))
            own['scope'] = CoreLib.transaction_scope_registry.get()
            own['session'] = self.transaction_widget_data_access.current_session()
            self.assertEqual([], self._run_in_threads([other_thread]))
            own['scope_after'] = CoreLib.transaction_scope_registry.get()

        request()

        self.assertIsNone(other_thread_saw['scope'])
        self.assertIsNot(own['session'], other_thread_saw['session'])
        self.assertIsNot(own['scope'], other_thread_saw['own_scope'])
        self.assertIs(own['scope'], own['scope_after'])           # still this thread's, untouched
        self.assertEqual(['mine'], self._names(SECRET_GROUP_ID))  # and it committed normally

    def test_sec4_a_transaction_alone_does_not_stop_two_requests_both_passing_a_check(self):
        # Documents the limit (AGENTS.md §6): a transaction makes writes all-or-nothing, it does not serialize a
        # check-then-write. Two requests both see the free slot and both take it. Use sec5's pattern instead.
        both_checked = threading.Barrier(2, timeout=WAIT_SECONDS)

        def take_the_slot(name: str):
            @Transaction()
            def check_then_write():
                is_free = not self._names(SLOT_GROUP_ID)
                both_checked.wait()
                if is_free:
                    self.transaction_widget_data_access.create(_widget(name, SLOT_GROUP_ID))
            return check_then_write

        errors = self._run_in_threads([take_the_slot('first'), take_the_slot('second')])

        self.assertEqual([], errors)
        self.assertEqual(['first', 'second'], self._names(SLOT_GROUP_ID))   # oversold: two rows for one slot

    def test_sec5_a_unique_index_lets_exactly_one_of_two_racing_requests_take_the_slot(self):
        both_checked = threading.Barrier(2, timeout=WAIT_SECONDS)

        @DuplicateErrorHandler()
        @Transaction()
        def take_the_slot():
            is_free = not self._names(SLOT_GROUP_ID)
            both_checked.wait()
            if is_free:
                self.transaction_widget_data_access.create(_widget('the-slot', SLOT_GROUP_ID))

        errors = self._run_in_threads([take_the_slot, take_the_slot])

        self.assertEqual(['the-slot'], self._names(SLOT_GROUP_ID))
        [refused] = errors
        self.assertIsInstance(refused, StatusCodeException)
        self.assertEqual(HTTPStatus.CONFLICT, refused.status_code)
        self.assertIsInstance(refused.__context__, IntegrityError)

    def test_sec6_a_failed_write_never_logs_the_values_it_wrote(self):
        handler = _KeepRecords()
        logging.getLogger(CONNECTION_LOGGER).addHandler(handler)
        self.addCleanup(logging.getLogger(CONNECTION_LOGGER).removeHandler, handler)
        self.transaction_widget_data_access.create(_widget(SECRET_VALUE, SECRET_GROUP_ID))

        @Transaction()
        def write_a_duplicate():
            self.transaction_widget_data_access.create(_widget(SECRET_VALUE, SECRET_GROUP_ID))

        duplicate = _widget(SECRET_VALUE, SECRET_GROUP_ID)
        with self.assertRaises(IntegrityError) as outside:
            self.transaction_widget_data_access.create(duplicate)
        with self.assertRaises(IntegrityError) as inside:
            write_a_duplicate()

        self.assertNotIn(SECRET_VALUE, str(outside.exception))   # nor the error a caller gets
        self.assertNotIn(SECRET_VALUE, str(inside.exception))

        # outside a transaction the commit's own error is not logged; inside, the rollback logs it once
        self.assertEqual(1, len(handler.messages))
        self.assertNotIn(SECRET_VALUE, handler.messages[0])

    def test_sec7_a_failing_query_never_shows_its_bound_values(self):
        @Transaction()
        def query_a_missing_table():
            with self.factory.get() as session:
                session.execute(text('SELECT * FROM missing_table WHERE name = :name'), {'name': SECRET_VALUE})

        with self.assertRaises(OperationalError) as raised:
            query_a_missing_table()

        self.assertNotIn(SECRET_VALUE, str(raised.exception))
        self.assertIn('missing_table', str(raised.exception))   # the statement itself is still there, to debug with

    def test_sec8_logging_every_query_never_prints_the_values_written(self):
        file_path = self.factory.engine.url.database
        logging_factory = SqlAlchemyConnectionFactory(OmegaConf.create({
            'create_db': False, 'log_queries': True,
            'session': {'pool_recycle': 3600, 'pool_pre_ping': False},
            'url': {'protocol': 'sqlite', 'file': file_path},
        }))
        self.addCleanup(logging_factory.engine.dispose)
        handler = _KeepRecords()
        engine_logger = logging.getLogger(SQLALCHEMY_ENGINE_LOGGER)
        engine_logger.addHandler(handler)
        self.addCleanup(engine_logger.removeHandler, handler)

        @Transaction()
        def write_a_secret():
            TransactionWidgetDataAccess(logging_factory).create(_widget(SECRET_VALUE, SECRET_GROUP_ID))

        write_a_secret()

        self.assertTrue(any('INSERT INTO' in message for message in handler.messages))   # the query was logged...
        self.assertEqual([], [message for message in handler.messages if SECRET_VALUE in message])   # ...not the value
        self.assertEqual([SECRET_VALUE], self._names(SECRET_GROUP_ID))
