"""What changes once DataAccess calls share one session: rows already loaded are not re-read, a changed
returned entity is saved, a second factory on the same database waits on the first, and work on other
threads is neither joined nor undone."""
import threading
import unittest

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from core_lib.connection.transaction_decorator import Transaction
from tests.test_data.test_utils import connect_to_file_db
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

    def test_e1_inside_a_transaction_get_returns_the_already_loaded_row(self):
        def load_rename_reload(keep_the_loaded_row: bool):
            widget_id = self.transaction_widget_data_access.create(_widget('acme')).id
            loaded = self.transaction_widget_data_access.get(widget_id)
            if not keep_the_loaded_row:
                loaded = None
            self._rename_raw(widget_id, 'renamed')
            return (self.transaction_widget_data_access.get(widget_id).name,
                    self.transaction_widget_data_access.names_in_group(GROUP_ID))

        in_transaction = Transaction()(load_rename_reload)
        self.assertEqual(('renamed', ['renamed']), load_rename_reload(True))
        self.transaction_widget_data_access.delete_group(GROUP_ID)

        # one session: while the loaded entity is referenced, get() answers from the session's identity
        # map; a column query, or a get() after the entity was dropped, reads the database
        self.assertEqual(('acme', ['renamed']), in_transaction(True))
        self.transaction_widget_data_access.delete_group(GROUP_ID)
        self.assertEqual(('renamed', ['renamed']), in_transaction(False))

    def test_e2_inside_a_transaction_a_changed_returned_entity_is_saved(self):
        def change_returned_entity(name: str) -> int:
            widget = self.transaction_widget_data_access.create(_widget(name))
            widget.name = name + '-changed-in-memory'
            self.transaction_widget_data_access.count_all()
            return widget.id

        outside_id = change_returned_entity('outside')
        inside_id = Transaction()(change_returned_entity)('inside')

        self.assertEqual('outside', self.transaction_widget_data_access.get(outside_id).name)
        self.assertEqual('inside-changed-in-memory', self.transaction_widget_data_access.get(inside_id).name)

    def test_e3_a_second_factory_on_the_same_database_waits_for_the_first(self):
        second_factory = connect_to_file_db(self, self.factory.engine.url.database)
        second_data_access = TransactionWidgetDataAccess(second_factory)

        def write_through_both():
            self.transaction_widget_data_access.create(_widget('first-factory'))
            second_data_access.create(_widget('second-factory'))

        write_through_both()
        self.assertEqual(['first-factory', 'second-factory'],
                         self.transaction_widget_data_access.names_in_group(GROUP_ID))
        self.transaction_widget_data_access.delete_group(GROUP_ID)

        # the first factory's session holds the write lock until the end; the second can only time out
        with self.assertRaises(OperationalError) as raised:
            Transaction()(write_through_both)()
        self.assertIn('locked', str(raised.exception))
        self.assertEqual(0, self.transaction_widget_data_access.count_all())

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

    def test_e5_a_row_another_thread_changes_mid_transaction_reads_stale_through_get(self):
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
            reads.append(self.transaction_widget_data_access.names_in_group(GROUP_ID))

        read_let_another_thread_rename_read_again()

        self.assertEqual(['acme', (False, []), 'acme', ['renamed']], reads)
        self.assertEqual('renamed', self.transaction_widget_data_access.get(widget_id).name)
