"""A generated project's requirements.txt asks for the core-lib extras its connections and caches need."""
import os
import shutil
import tempfile
import unittest

from omegaconf import OmegaConf

from core_lib_generator.core_lib_generator_from_yaml import CoreLibGenerator

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE_YAML = os.path.join(REPO_ROOT, 'core_lib_generator', 'ExampleCoreLib.yaml')

SQL_FACTORY = 'core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory'


def sql_connection(key: str, protocol: str) -> dict:
    return {'key': key, 'type': SQL_FACTORY, 'config': {'url': {'protocol': protocol}}}


class TestGenerateRequirements(unittest.TestCase):

    def setUp(self):
        self.output_folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.output_folder)

    def _requirements(self, config) -> str:
        original_cwd = os.getcwd()
        try:
            os.chdir(self.output_folder)
            generator = CoreLibGenerator(config)
            generator.generate_requirements()
            with open(os.path.join(generator.snake_core_lib_name, 'requirements.txt')) as requirements:
                return requirements.read()
        finally:
            os.chdir(original_cwd)

    def _config(self, connections: list, caches: list = None):
        return OmegaConf.create({'core_lib': {'name': 'AcmeCoreLib', 'connections': connections, 'caches': caches or []}})

    def test_shipped_example_asks_for_its_backends(self):
        # ExampleCoreLib.yaml: PostgreSQL, Solr and Neo4j connections, and an in-memory cache.
        self.assertEqual('core-lib[neo4j,postgres,solr]', self._requirements(OmegaConf.load(EXAMPLE_YAML)))

    def test_sqlite_and_memory_cache_need_no_extra(self):
        config = self._config([sql_connection('widget_db', 'sqlite')], [{'key': 'acme_cache', 'type': 'memory'}])

        self.assertEqual('core-lib', self._requirements(config))

    def test_mysql_a_driver_suffix_and_caches_map_to_their_extras(self):
        config = self._config(
            [sql_connection('orders_db', 'mysql'), sql_connection('ledger_db', 'postgresql+psycopg2')],
            [{'key': 'sessions', 'type': 'redis'}, {'key': 'pages', 'type': 'memcached'}],
        )

        self.assertEqual('core-lib[memcached,mysql,postgres,redis]', self._requirements(config))

    def test_connection_written_by_the_interactive_generator(self):
        # `core_lib generate` without --yaml writes `url` directly on the connection, with no `config` level.
        connection = {'key': 'widget_db', 'type': SQL_FACTORY, 'url': {'protocol': 'postgresql'}}

        self.assertEqual('core-lib[postgres]', self._requirements(self._config([connection])))

    def test_same_extra_is_asked_for_once(self):
        config = self._config([sql_connection('first_db', 'postgresql'), sql_connection('second_db', 'postgresql')])

        self.assertEqual('core-lib[postgres]', self._requirements(config))
