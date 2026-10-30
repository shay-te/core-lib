"""ConnectionFactoryRegistry.get_or_reg builds a connection factory from config once per `_instance_key_` and hands
every later caller that same factory, so libraries composed over one database share one engine. Without an instance
key it builds a new, unregistered factory on every call."""
import os
import shutil
import tempfile
import unittest

from omegaconf import OmegaConf

from core_lib.connection.connection_factory_registry import ConnectionFactoryRegistry
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.helpers.constants import InstantiateConfigConstants

SQLALCHEMY_FACTORY_TARGET = 'core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory'
INSTANCE_KEY = InstantiateConfigConstants.INSTANCE_KEY.value
TARGET = InstantiateConfigConstants.TARGET.value


class TestConnectionFactoryRegistry(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.registry = ConnectionFactoryRegistry()
        self.factories = []

    def tearDown(self):
        for factory in self.factories:
            factory.connection.close()
            factory.engine.dispose()
        shutil.rmtree(self.folder)

    def _db_file(self, name: str) -> str:
        # build_url strips a leading '/', so a SQLite file is given relative to the working directory.
        return os.path.relpath(os.path.join(self.folder, name))

    def _sqlite_config(self, db_file: str, instance_key: str = None):
        config = {
            TARGET: SQLALCHEMY_FACTORY_TARGET,
            'config': {'create_db': False, 'url': {'protocol': 'sqlite', 'file': db_file}},
        }
        if instance_key:
            config[INSTANCE_KEY] = instance_key
        return OmegaConf.create(config)

    def _get_or_reg(self, config):
        factory = self.registry.get_or_reg(config)
        if factory not in self.factories:
            self.factories.append(factory)
        return factory

    def test_same_instance_key_returns_the_factory_built_first(self):
        acme_db = self._db_file('acme.db')
        other_db = self._db_file('other.db')
        acme_config = self._sqlite_config(acme_db, 'acme_db')

        first_factory = self._get_or_reg(acme_config)
        second_factory = self._get_or_reg(self._sqlite_config(other_db, 'acme_db'))

        self.assertIsInstance(first_factory, SqlAlchemyConnectionFactory)
        self.assertIs(first_factory, second_factory)
        self.assertEqual(acme_db, first_factory.engine.url.database)
        self.assertFalse(os.path.exists(other_db))  # the second config was never built
        self.assertEqual(['acme_db'], self.registry.registered())
        self.assertEqual('acme_db', acme_config[INSTANCE_KEY])  # the caller's config is left as it was

    def test_two_instance_keys_build_two_factories(self):
        acme_factory = self._get_or_reg(self._sqlite_config(self._db_file('acme.db'), 'acme_db'))
        widget_factory = self._get_or_reg(self._sqlite_config(self._db_file('widget.db'), 'widget_db'))

        self.assertIsNot(acme_factory, widget_factory)
        self.assertIs(widget_factory, self.registry.get('widget_db'))
        self.assertEqual(['acme_db', 'widget_db'], self.registry.registered())

    def test_config_without_instance_key_builds_a_new_unregistered_factory_every_call(self):
        config = self._sqlite_config(self._db_file('acme.db'))

        with self.assertLogs('core_lib.connection.connection_factory_registry', level='WARNING') as logs:
            first_factory = self._get_or_reg(config)
            second_factory = self._get_or_reg(config)

        self.assertIsInstance(first_factory, SqlAlchemyConnectionFactory)
        self.assertIsNot(first_factory, second_factory)
        self.assertEqual([], self.registry.registered())
        self.assertEqual(2, len(logs.records))

    def test_config_without_instance_key_or_target_is_refused(self):
        with self.assertRaisesRegex(ValueError, '_instance_key_ and _target_ not found in the config'):
            self.registry.get_or_reg(OmegaConf.create({'config': {'url': {'protocol': 'sqlite'}}}))
        self.assertEqual([], self.registry.registered())

    def test_instance_key_without_target_is_refused_and_registers_nothing(self):
        config = OmegaConf.create({INSTANCE_KEY: 'acme_db', 'config': {'url': {'protocol': 'sqlite'}}})

        with self.assertRaisesRegex(ValueError, 'register object is not of type'):
            self.registry.get_or_reg(config)
        self.assertEqual([], self.registry.registered())
