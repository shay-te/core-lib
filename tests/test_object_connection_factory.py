"""ObjectConnectionFactory wraps any object in the `with factory.get() as obj:` shape: without callbacks every block
gets the wrapped object itself; with callbacks every block gets what the open callback returned, and the close
callback runs when the block exits, even when it raised."""
import os
import shutil
import sqlite3
import tempfile
import unittest

from core_lib.connection.object_connection_factory import ObjectConnectionFactory


def close_connection(connection: sqlite3.Connection):
    connection.close()


class TestObjectConnectionFactory(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.db_path = os.path.join(self.folder, 'acme.db')

    def tearDown(self):
        shutil.rmtree(self.folder)

    def test_without_callbacks_every_block_gets_the_wrapped_object(self):
        store = {'widgets': {}}
        factory = ObjectConnectionFactory(store)

        with factory.get() as first_store:
            first_store['widgets'][1] = 'widget'
        with factory.get() as second_store:
            self.assertIs(store, second_store)

        self.assertIs(store, first_store)
        self.assertIs(store, factory.object)
        self.assertEqual({'widgets': {1: 'widget'}}, store)

    def test_callbacks_open_a_connection_per_block_and_close_it_when_the_block_exits(self):
        factory = ObjectConnectionFactory(
            self.db_path, new_session_callback=sqlite3.connect, close_session_callback=close_connection
        )

        with factory.get() as first_connection:
            first_connection.execute('CREATE TABLE acme_widget (name TEXT)')
            first_connection.execute("INSERT INTO acme_widget (name) VALUES ('widget')")
            first_connection.commit()
        with self.assertRaises(sqlite3.ProgrammingError):  # closed when its block exited
            first_connection.execute('SELECT 1')

        with factory.get() as second_connection:
            self.assertIsNot(first_connection, second_connection)
            self.assertEqual([('widget',)], second_connection.execute('SELECT name FROM acme_widget').fetchall())

        self.assertEqual(self.db_path, factory.object)  # the wrapped object, not what a callback opened

    def test_close_callback_runs_when_the_block_raises_and_the_error_reaches_the_caller(self):
        closed = []
        store = {'name': 'widget'}
        factory = ObjectConnectionFactory(store, close_session_callback=closed.append)

        with self.assertRaisesRegex(ValueError, 'widget failed'):
            with factory.get():
                raise ValueError('widget failed')

        self.assertEqual(1, len(closed))
        self.assertIs(store, closed[0])
