"""Sharing one session must not change what DataAccess code sees: a row is read again from the
database, a returned row changed in memory is not saved, two factories on one database share the
connection, and work on other threads is neither joined nor undone."""
import threading
import unittest

from sqlalchemy import text

from core_lib.connection.transaction_decorator import Transaction
from tests.test_data.engine_event_counter import EngineEventCounter
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_file_db, connect_to_mem_db
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 8
WAIT_SECONDS = 10
RAW_RENAME = text('UPDATE transaction_widget SET name = :name WHERE id = :id')


def _widget(name: str) -> dict:
    return {TransactionWidget.group_id.key: GROUP_ID, TransactionWidget.name.key: name}


class TestTransactionEdgeCases(unittest.TestCase):

    def setUp(self):
        self.factory = connect_to_file_db(self)
        self.transaction_widget_data_access = TransactionWidgetDataAccess(self.factory)

    def _run_in_thread(self, function):
        errors = []

        def run():
            try:
                function()
            except BaseException as error:
                errors.append(error)

        worker = threading.Thread(target=run)
        worker.start()
        return worker, errors

    def _rename_raw(self, widget_id: int, name: str):
        # a write the ORM does not track: raw SQL, or a bulk update with synchronize_session=False
        with self.factory.get() as session:
            session.execute(RAW_RENAME, {'name': name, 'id': widget_id})

    def test_e1_get_reads_the_database_again_even_while_the_loaded_row_is_held(self):
        def load_rename_reload():
            widget_id = self.transaction_widget_data_access.create(_widget('acme')).id
            loaded = self.transaction_widget_data_access.get(widget_id)
            self._rename_raw(widget_id, 'renamed')
            return loaded.name, self.transaction_widget_data_access.get(widget_id).name

        self.assertEqual(('acme', 'renamed'), load_rename_reload())
        self.transaction_widget_data_access.delete_group(GROUP_ID)
        self.assertEqual(('acme', 'renamed'), Transaction()(load_rename_reload)())

    def test_e2_a_returned_row_changed_in_memory_is_not_saved(self):
        def change_returned_entity(name: str) -> int:
            widget = self.transaction_widget_data_access.create(_widget(name))
            widget.name = name + '-changed-in-memory'
            self.transaction_widget_data_access.count_all()
            return widget.id

        outside_id = change_returned_entity('outside')
        inside_id = Transaction()(change_returned_entity)('inside')

        self.assertEqual('outside', self.transaction_widget_data_access.get(outside_id).name)
        self.assertEqual('inside', self.transaction_widget_data_access.get(inside_id).name)

    def test_e3_two_factories_on_one_database_share_the_connection(self):
        second_factory = connect_to_file_db(self, self.factory.engine.url.database)
        second_data_access = TransactionWidgetDataAccess(second_factory)
        sessions = []
        self.assertEqual(self.factory, second_factory)
        self.assertEqual(hash(self.factory), hash(second_factory))
        self.assertEqual(1, len({self.factory, second_factory}))

        @Transaction()
        def write_through_both(should_fail: bool):
            sessions.append(self.transaction_widget_data_access.current_session())
            self.transaction_widget_data_access.create(_widget('first-factory'))
            sessions.append(second_data_access.current_session())
            second_data_access.create(_widget('second-factory'))
            if should_fail:
                raise RuntimeError('roll both back')

        with self.assertRaises(RuntimeError):
            write_through_both(True)
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

        with EngineEventCounter(self.factory.engine) as first_engine, \
                EngineEventCounter(second_factory.engine) as second_engine:
            write_through_both(False)

        self.assertIs(sessions[2], sessions[3])
        self.assertEqual((1, 0), (first_engine.commits, second_engine.commits))
        self.assertEqual(['first-factory', 'second-factory'],
                         self.transaction_widget_data_access.names_in_group(GROUP_ID))

    def test_e3_in_memory_databases_and_other_backends_stay_separate_connections(self):
        first_factory, second_factory = connect_to_mem_db(), connect_to_mem_db()
        first_data_access = TransactionWidgetDataAccess(first_factory)
        second_data_access = TransactionWidgetDataAccess(second_factory)
        other_backend = RecordingConnectionFactory()
        # the same URL, yet two databases: never equal to each other, always equal to itself
        self.assertNotEqual(first_factory, second_factory)
        self.assertTrue(first_factory == first_factory)  # NOSONAR - compares the factory with itself on purpose
        self.assertNotEqual(first_factory, other_backend)  # another kind of factory is never equal

        @Transaction()
        def write_to_each():
            first_data_access.create(_widget('first-database'))
            second_data_access.create(_widget('second-database'))
            with other_backend.get():
                pass
            return first_data_access.current_session() is second_data_access.current_session()

        self.assertFalse(write_to_each())
        self.assertEqual(1, len(other_backend.created))
        self.assertEqual(['first-database'], first_data_access.names_in_group(GROUP_ID))
        self.assertEqual(['second-database'], second_data_access.names_in_group(GROUP_ID))

    def test_e4_a_background_write_waits_for_the_transaction_and_survives_its_rollback(self):
        started = threading.Event()
        workers = []

        @Transaction()
        def write_start_background_write_then_fail():
            self.transaction_widget_data_access.create(_widget('transaction-row'))
            workers.append(self._run_in_thread(
                lambda: (started.set(), self.transaction_widget_data_access.create(_widget('background-row')))))
            self.assertTrue(started.wait(WAIT_SECONDS))
            raise RuntimeError('the transaction fails')

        with self.assertRaises(RuntimeError):
            write_start_background_write_then_fail()
        [(worker, errors)] = workers
        worker.join(WAIT_SECONDS)

        self.assertFalse(worker.is_alive())
        self.assertEqual([], errors)
        self.assertEqual(['background-row'], self.transaction_widget_data_access.names_in_group(GROUP_ID))

    def test_e5_a_row_another_thread_changes_mid_transaction_is_read_fresh(self):
        widget_id = self.transaction_widget_data_access.create(_widget('acme')).id
        reads = []

        @Transaction()
        def read_let_another_thread_rename_read_again():
            loaded = self.transaction_widget_data_access.get(widget_id)
            reads.append(loaded.name)
            worker, errors = self._run_in_thread(
                lambda: self.transaction_widget_data_access.update(widget_id, {TransactionWidget.name.key: 'renamed'}))
            worker.join(WAIT_SECONDS)
            reads.append((worker.is_alive(), errors))
            reads.append(self.transaction_widget_data_access.get(widget_id).name)

        read_let_another_thread_rename_read_again()

        self.assertEqual(['acme', (False, []), 'renamed'], reads)
