"""SqlAlchemyConnectionFactory.identity(), and the __eq__ / __hash__ the TransactionalConnectionFactory base builds
from it: factories on one database have one identity, so a transaction gives them one session; an in-memory sqlite is
a database per engine; the identity is always a str and never shows a password; anything else is never equal."""
import copy
import os
import shutil
import tempfile
import unittest
from unittest import mock

from omegaconf import OmegaConf
from sqlalchemy.engine import Engine

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.connection.transaction_decorator import Transaction
from tests.test_data.recording_connection_factory import RecordingConnectionFactory
from tests.test_data.test_utils import connect_to_mem_db, connect_to_mongo
from tests.test_data.transaction_widget import TransactionWidget
from tests.test_data.transaction_widget_data_access import TransactionWidgetDataAccess

GROUP_ID = 71
SERVER_URL = {'protocol': 'postgresql', 'username': 'acme', 'password': 'one', 'host': 'db.example.com',
              'port': 5432, 'file': 'widgets'}


class _SubclassedFactory(SqlAlchemyConnectionFactory):
    pass


def _factory(url: dict, factory_class=SqlAlchemyConnectionFactory) -> SqlAlchemyConnectionFactory:
    config = OmegaConf.create({'create_db': url['protocol'] == 'sqlite', 'log_queries': False,
                               'session': {'pool_recycle': 3600, 'pool_pre_ping': False}, 'url': url})
    if url['protocol'] == 'sqlite':
        return factory_class(config)
    with mock.patch.object(Engine, 'connect'):   # a server URL: build the real engine, never connect to it
        return factory_class(config)


class TestSqlAlchemyConnectionFactoryEquality(unittest.TestCase):

    def setUp(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory, True)
        self.file_a = os.path.relpath(os.path.join(directory, 'a.db'))
        self.file_b = os.path.relpath(os.path.join(directory, 'b.db'))

    def _sqlite(self, file_path: str = None, factory_class=SqlAlchemyConnectionFactory) -> SqlAlchemyConnectionFactory:
        url = {'protocol': 'sqlite'} if file_path is None else {'protocol': 'sqlite', 'file': file_path}
        factory = _factory(url, factory_class)
        self.addCleanup(factory.engine.dispose)
        self.addCleanup(factory.connection.close)
        return factory

    def _server(self, **changes) -> SqlAlchemyConnectionFactory:
        factory = _factory(dict(SERVER_URL, **changes))
        self.addCleanup(factory.engine.dispose)
        return factory

    def _assert_equal_both_ways(self, left, right):
        self.assertEqual(left, right)
        self.assertEqual(right, left)
        self.assertEqual(hash(left), hash(right))   # equal objects must hash alike

    def _assert_not_equal_both_ways(self, left, right):
        self.assertNotEqual(left, right)
        self.assertNotEqual(right, left)

    # __eq__

    def test_q1_every_kind_of_factory_equals_itself(self):
        for factory in (self._sqlite(self.file_a), self._sqlite(), self._sqlite(':memory:'), self._server()):
            self.assertTrue(factory == factory)   # NOSONAR - compares the factory with itself on purpose
            self.assertFalse(factory != factory)  # NOSONAR - compares the factory with itself on purpose

    def test_q2_factories_on_one_file_are_equal_symmetric_and_transitive(self):
        first, second, third = self._sqlite(self.file_a), self._sqlite(self.file_a), self._sqlite(self.file_a)

        for left, right in ((first, second), (second, third), (first, third)):
            self._assert_equal_both_ways(left, right)

    def test_q3_factories_on_different_files_are_not_equal(self):
        self._assert_not_equal_both_ways(self._sqlite(self.file_a), self._sqlite(self.file_b))

    def test_q4_in_memory_engines_are_never_equal_to_each_other_in_any_spelling(self):
        spellings = (None, ':memory:', 'file::memory:?uri=true', 'file:widgets?mode=memory&uri=true')
        first_engines = [self._sqlite(spelling) for spelling in spellings]
        second_engines = [self._sqlite(spelling) for spelling in spellings]

        for i, left in enumerate(first_engines):
            self._assert_not_equal_both_ways(left, second_engines[i])   # the same spelling, another engine
            for right in first_engines[i + 1:]:
                self._assert_not_equal_both_ways(left, right)          # another spelling

    def test_q5_a_copy_of_an_in_memory_factory_shares_its_engine_so_it_is_the_same_database(self):
        factory = self._sqlite()
        copied = copy.copy(factory)

        self.assertIs(factory.engine, copied.engine)
        self._assert_equal_both_ways(factory, copied)

    def test_q6_a_file_factory_and_an_in_memory_factory_are_not_equal(self):
        self._assert_not_equal_both_ways(self._sqlite(self.file_a), self._sqlite())
        self._assert_not_equal_both_ways(self._sqlite(self.file_a), self._sqlite(':memory:'))

    def test_q7_a_factory_never_equals_anything_that_is_not_a_sqlalchemy_factory(self):
        factory = self._sqlite(self.file_a)
        others = [None, 0, '', str(factory.engine.url), factory.engine.url, factory.engine, object(), mock.Mock(),
                  RecordingConnectionFactory(), connect_to_mongo()]

        for other in others:
            self._assert_not_equal_both_ways(factory, other)
            self.assertIs(False, factory.__eq__(other))   # a plain False, never an exception

    def test_q8_a_subclass_on_the_same_database_is_equal_both_ways(self):
        self._assert_equal_both_ways(self._sqlite(self.file_a), self._sqlite(self.file_a, _SubclassedFactory))
        self._assert_not_equal_both_ways(self._sqlite(), self._sqlite(factory_class=_SubclassedFactory))

    def test_q9_server_factories_are_equal_only_when_user_host_port_database_and_driver_match(self):
        base = self._server()

        self._assert_equal_both_ways(base, self._server())
        for changes in ({'username': 'other'}, {'host': 'other.example.com'}, {'port': 5433},
                        {'file': 'other_widgets'}, {'protocol': 'postgresql+psycopg2'}):
            self._assert_not_equal_both_ways(base, self._server(**changes))

    def test_q10_one_database_through_two_url_spellings_is_two_databases_to_the_factory(self):
        # Documents the limit ("one database, one URL"): equality compares URLs, not where they lead.
        self._assert_not_equal_both_ways(self._sqlite(self.file_a), self._sqlite(os.path.join('.', self.file_a)))
        self._assert_not_equal_both_ways(self._server(host='db.example.com'), self._server(host='DB.EXAMPLE.COM'))

    # __hash__

    def test_h1_equal_factories_always_hash_alike(self):
        pairs = [(self._sqlite(self.file_a), self._sqlite(self.file_a)),
                 (self._sqlite(self.file_a), self._sqlite(self.file_a, _SubclassedFactory)),
                 (self._server(), self._server())]
        memory = self._sqlite()
        pairs.append((memory, copy.copy(memory)))

        for left, right in pairs:
            self.assertEqual(left, right)
            self.assertEqual(hash(left), hash(right))

    def test_h2_the_hash_never_changes_while_a_factory_lives(self):
        factory = self._sqlite(self.file_a)
        before = hash(factory)
        data_access = TransactionWidgetDataAccess(factory)

        Transaction()(lambda: data_access.create({TransactionWidget.group_id.key: GROUP_ID,
                                                   TransactionWidget.name.key: 'used'}))()
        after_use = hash(factory)
        factory.engine.dispose()

        self.assertEqual((before, before), (after_use, hash(factory)))

    def test_h3_a_set_and_a_dict_merge_equal_factories_and_keep_the_rest_apart(self):
        file_a, file_a_again, file_b = self._sqlite(self.file_a), self._sqlite(self.file_a), self._sqlite(self.file_b)
        memory, other_memory = self._sqlite(), self._sqlite()

        self.assertEqual(4, len({file_a, file_a_again, file_b, memory, other_memory}))
        by_factory = {file_a: 'a', file_b: 'b', memory: 'memory'}
        self.assertEqual('a', by_factory[file_a_again])   # found through an equal, different factory
        self.assertNotIn(other_memory, by_factory)

    def test_h4_in_memory_factories_each_have_their_own_identity_and_a_set_keeps_them_apart(self):
        memories = [self._sqlite() for i in range(5)]

        self.assertEqual(5, len({memory.identity() for memory in memories}))   # the same URL, five engines
        self.assertEqual(5, len(set(memories)))

    def test_h5_urls_with_query_parameters_hash_and_compare_whatever_their_order(self):
        first = self._server(file='widgets?sslmode=require&connect_timeout=5')
        reordered = self._server(file='widgets?connect_timeout=5&sslmode=require')

        self._assert_equal_both_ways(first, reordered)

    def test_h6_a_password_is_never_part_of_the_identity_and_never_shown_in_it(self):
        one, two = self._server(password='secret-one'), self._server(password='secret-two')

        self._assert_equal_both_ways(one, two)   # the same user on the same database: one identity
        for factory in (one, two):
            self.assertNotIn('secret', factory.identity())
            self.assertIn('acme:***@', factory.identity())

    def test_h9_the_identity_is_always_a_str_naming_what_the_connections_reach(self):
        factories = [self._sqlite(self.file_a), self._sqlite(), self._sqlite(':memory:'),
                     self._sqlite('file::memory:?uri=true'), self._sqlite('file:widgets?mode=memory&uri=true'),
                     self._server(), self._server(file='widgets?sslmode=require')]

        for factory in factories:
            identity = factory.identity()
            self.assertIs(str, type(identity))
            self.assertEqual(identity, factory.identity())   # stable
        self.assertIn(self.file_a, factories[0].identity())
        self.assertTrue(factories[5].identity().startswith('postgresql://acme:***@db.example.com:5432/widgets'))

    def test_h10_a_copied_in_memory_factory_has_its_originals_identity(self):
        factory = self._sqlite()

        self.assertEqual(factory.identity(), copy.copy(factory).identity())
        self.assertNotEqual(factory.identity(), self._sqlite().identity())

    def test_h7_two_in_memory_databases_in_one_transaction_get_their_own_sessions(self):
        first, second = TransactionWidgetDataAccess(self._sqlite()), TransactionWidgetDataAccess(self._sqlite())

        @Transaction()
        def write_each():
            first.create({TransactionWidget.group_id.key: GROUP_ID, TransactionWidget.name.key: 'first'})
            second.create({TransactionWidget.group_id.key: GROUP_ID, TransactionWidget.name.key: 'second'})
            return first.current_session() is second.current_session()

        self.assertFalse(write_each())
        self.assertEqual((['first'], ['second']), (first.names_in_group(GROUP_ID), second.names_in_group(GROUP_ID)))

    def test_h8_a_copied_in_memory_factory_joins_the_same_session_in_a_transaction(self):
        factory = self._sqlite()
        original, copied = TransactionWidgetDataAccess(factory), TransactionWidgetDataAccess(copy.copy(factory))

        @Transaction()
        def write_through_both():
            original.create({TransactionWidget.group_id.key: GROUP_ID, TransactionWidget.name.key: 'original'})
            copied.create({TransactionWidget.group_id.key: GROUP_ID, TransactionWidget.name.key: 'copied'})
            return original.current_session() is copied.current_session()

        self.assertTrue(write_through_both())
        self.assertEqual(['copied', 'original'], original.names_in_group(GROUP_ID))
