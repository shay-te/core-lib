import unittest
from unittest.mock import MagicMock, patch

from omegaconf import OmegaConf

from core_lib.connection.connection_factory_registry import ConnectionFactoryRegistry
from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.mongodb_connection_factory import MongoDBConnectionFactory
from core_lib.connection.neo4j_connection import Neo4jConnection
from core_lib.connection.object_connection import ObjectConnection
from core_lib.connection.object_connection_factory import ObjectConnectionFactory
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory


class _FakeFactory(ConnectionFactory):
    def get(self, *args, **kwargs):
        """
        Return a fake connection object for testing purposes.
        """
        return 'connection'


class TestConnectionFactoryRegistry(unittest.TestCase):
    def test_get_or_reg_warns_when_no_instance_key(self):
        registry = ConnectionFactoryRegistry()
        config = OmegaConf.create(
            {'_target_': 'tests.test_connections_full._FakeFactory'}
        )
        instance = registry.get_or_reg(config)
        self.assertIsInstance(instance, _FakeFactory)

    def test_get_or_reg_raises_when_neither_keys(self):
        registry = ConnectionFactoryRegistry()
        config = OmegaConf.create({'foo': 'bar'})
        with self.assertRaises(ValueError):
            registry.get_or_reg(config)

    def test_get_or_reg_registers_and_returns_cached(self):
        registry = ConnectionFactoryRegistry()
        config = OmegaConf.create(
            {
                '_instance_key_': 'fake',
                '_target_': 'tests.test_connections_full._FakeFactory',
            }
        )
        instance = registry.get_or_reg(config)
        self.assertIsInstance(instance, _FakeFactory)
        # Same instance returned on second call
        self.assertIs(registry.get_or_reg(config), instance)


class TestMongoDBConnectionFactory(unittest.TestCase):
    def test_client_property(self):
        config = OmegaConf.create(
            {'url': {'protocol': 'mongodb', 'host': 'localhost', 'port': 27017}}
        )
        with patch(
            'core_lib.connection.mongodb_connection_factory.pymongo.MongoClient'
        ) as mock_mongo:
            mock_client = MagicMock()
            mock_mongo.return_value = mock_client
            factory = MongoDBConnectionFactory(config)
            self.assertIs(factory.client, mock_client)


class TestNeo4jConnection(unittest.TestCase):
    def test_enter_returns_session(self):
        session = MagicMock()
        conn = Neo4jConnection(session)
        with conn as s:
            self.assertIs(s, session)
        session.close.assert_called_once_with()


class TestObjectConnection(unittest.TestCase):
    def test_close_callback_invoked_with_obj(self):
        cb = MagicMock()
        obj = object()
        conn = ObjectConnection(obj, cb)
        with conn as o:
            self.assertIs(o, obj)
        cb.assert_called_once_with(obj)

    def test_no_callback_skip(self):
        conn = ObjectConnection('obj', None)
        with conn as o:
            self.assertEqual(o, 'obj')


class TestObjectConnectionFactory(unittest.TestCase):
    def test_object_property(self):
        f = ObjectConnectionFactory('the-object')
        self.assertEqual(f.object, 'the-object')

    def test_get_with_callback_creates_new_obj(self):
        new_cb = MagicMock(return_value='new-obj')
        close_cb = MagicMock()
        f = ObjectConnectionFactory('orig', new_session_callback=new_cb, close_session_callback=close_cb)
        conn = f.get()
        new_cb.assert_called_once_with('orig')
        with conn as o:
            self.assertEqual(o, 'new-obj')
        close_cb.assert_called_once_with('new-obj')


class TestSqlAlchemyConnectionFactory(unittest.TestCase):
    def test_unsupported_pool_skips_extra_params(self):
        config = OmegaConf.create(
            {
                'log_queries': False,
                'create_db': False,
                'session': {
                    'pool_recycle': 100,
                    'pool_pre_ping': False,
                    'pool_size': 1,
                    'max_overflow': 2,
                },
                'url': {
                    'protocol': 'sqlite',
                    'username': None,
                    'password': None,
                    'host': None,
                    'port': None,
                    'file': None,
                },
            }
        )
        with patch(
            'core_lib.connection.sql_alchemy_connection_factory.create_engine'
        ) as mock_ce, patch(
            'core_lib.connection.sql_alchemy_connection_factory.Base'
        ):
            mock_ce.return_value = MagicMock()
            factory = SqlAlchemyConnectionFactory(config)
            kwargs = mock_ce.call_args.kwargs
            self.assertNotIn('pool_size', kwargs)
            self.assertNotIn('max_overflow', kwargs)
            self.assertIsNotNone(factory.connection)

    def test_supported_pool_passes_extra(self):
        config = OmegaConf.create(
            {
                'log_queries': True,
                'create_db': True,
                'session': {
                    'pool_recycle': 100,
                    'pool_pre_ping': True,
                    'pool_size': 7,
                    'max_overflow': 9,
                },
                'url': {
                    'protocol': 'postgresql',
                    'username': 'u',
                    'password': 'p',  # NOSONAR URL-builder fixture, not a credential.
                    'host': 'h',
                    'port': 5432,
                    'file': None,
                },
            }
        )
        with patch(
            'core_lib.connection.sql_alchemy_connection_factory.create_engine'
        ) as mock_ce, patch(
            'core_lib.connection.sql_alchemy_connection_factory.Base'
        ) as mock_base:
            mock_engine = MagicMock()
            mock_ce.return_value = mock_engine
            SqlAlchemyConnectionFactory(config)
            kwargs = mock_ce.call_args.kwargs
            self.assertEqual(kwargs['pool_size'], 7)
            self.assertEqual(kwargs['max_overflow'], 9)
            mock_base.metadata.create_all.assert_called_once_with(mock_engine)
