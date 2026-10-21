"""`core_lib generate` asks about database connections; each answer becomes a connection of the library's YAML."""
import unittest

from core_lib_generator.config_collectors.database import generate_db_template
from tests.test_data.test_utils import typed

SQL_FACTORY = 'core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory'


class TestDatabaseCollector(unittest.TestCase):

    def test_sqlite_with_every_default(self):
        # name, then Enter for: type [1-SQLite], log queries [no], create db [yes], pool recycle [3200],
        # pool pre ping [no], migration [no], another connection [no]. SQLite asks nothing about a server.
        with typed('acme_db', '', '', '', '', '', '', ''):
            connections = generate_db_template()

        self.assertEqual({
            'acme_db': {
                'env': {},
                'connection': {
                    'type': SQL_FACTORY,
                    'key': 'acme_db',
                    'migrate': False,
                    'log_queries': False,
                    'create_db': True,
                    'session': {'pool_recycle': 3200, 'pool_pre_ping': False},
                    'url': {'protocol': 'sqlite'},
                },
            },
        }, connections)

    def test_server_database_reads_its_url_from_env_variables_named_after_the_connection(self):
        # 2-Postgresql; every setting typed; Enter keeps the PostgreSQL port; an empty password is asked again.
        with typed('acme_db', '2', 'yes', 'no', '1800', 'yes', 'yes', '', 'db.acme.example', 'reviewer', '', 's3cret',
                   'no'):
            connections = generate_db_template()

        self.assertEqual({
            'acme_db': {
                'env': {
                    'ACME_DB_DB': 'acme_db',
                    'ACME_DB_USER': 'reviewer',
                    'ACME_DB_PASSWORD': 's3cret',
                    'ACME_DB_PORT': 5432,
                    'ACME_DB_HOST': 'db.acme.example',
                },
                'connection': {
                    'type': SQL_FACTORY,
                    'key': 'acme_db',
                    'migrate': True,
                    'log_queries': True,
                    'create_db': False,
                    'session': {'pool_recycle': 1800, 'pool_pre_ping': True},
                    'url': {
                        'file': '${oc.env:ACME_DB_DB}',
                        'protocol': 'postgresql',
                        'username': '${oc.env:ACME_DB_USER}',
                        'password': '${oc.env:ACME_DB_PASSWORD}',
                        'port': '${oc.env:ACME_DB_PORT}',
                        'host': '${oc.env:ACME_DB_HOST}',
                    },
                },
            },
        }, connections)

    def test_each_server_database_offers_its_standard_port(self):
        expected = {
            '2': ('postgresql', 5432),
            '3': ('mysql', 3306),
            '4': ('oracle', 1521),
            '5': ('mssql', 1433),
            '6': ('firebird', 3050),
            '7': ('sybase', 5000),
        }
        for db_type, (protocol, port) in expected.items():
            with self.subTest(protocol=protocol):
                # Enter for every setting, the server port, host and user; a password must be typed
                with typed('acme_db', db_type, '', '', '', '', '', '', '', '', 's3cret', ''):
                    connection = generate_db_template()['acme_db']

                self.assertEqual({
                    'file': '${oc.env:ACME_DB_DB}',
                    'protocol': protocol,
                    'username': '${oc.env:ACME_DB_USER}',
                    'password': '${oc.env:ACME_DB_PASSWORD}',
                    'port': '${oc.env:ACME_DB_PORT}',
                    'host': '${oc.env:ACME_DB_HOST}',
                }, connection['connection']['url'])
                self.assertEqual({
                    'ACME_DB_DB': 'acme_db',
                    'ACME_DB_USER': 'user',
                    'ACME_DB_PASSWORD': 's3cret',
                    'ACME_DB_PORT': port,
                    'ACME_DB_HOST': 'localhost',
                }, connection['env'])

    def test_second_connection_cannot_reuse_a_name(self):
        sqlite_defaults = ('', '', '', '', '', '')   # type, log queries, create db, pool recycle, pre ping, migration
        with typed('acme_db', *sqlite_defaults, 'yes', 'acme_db', 'ledger_db', *sqlite_defaults, 'no'):
            connections = generate_db_template()

        self.assertEqual(['acme_db', 'ledger_db'], list(connections))
        self.assertEqual('ledger_db', connections['ledger_db']['connection']['key'])
