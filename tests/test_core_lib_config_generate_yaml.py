"""The interactive questions of `core_lib generate` write one YAML file that describes the library to generate."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from omegaconf import OmegaConf

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_FACTORY = 'core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory'
RUN_AND_PRINT_FILE_NAME = (
    'from core_lib_generator.core_lib_config_generate_yaml import generate_core_lib_yaml\n'
    'print(generate_core_lib_yaml())\n'
)
SQLITE_CONNECTION = ('acme_db', '', '', '', '', '', '', '')   # name, then Enter for every SQLite setting and "another?"


class TestCoreLibConfigGenerateYaml(unittest.TestCase):

    def _answer(self, *lines, python_args=('-c', RUN_AND_PRINT_FILE_NAME)) -> tuple:
        # The module collects the answers in module-level state, so, like `core_lib generate`, each run gets its own
        # interpreter. What it reads is real stdin.
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        result = subprocess.run(
            [sys.executable, *python_args],
            input=''.join(f'{line}\n' for line in lines),
            cwd=folder,
            env=dict(os.environ, PYTHONPATH=REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return result.stdout, folder

    def _load(self, folder: str, file_name: str) -> dict:
        return OmegaConf.to_container(OmegaConf.load(os.path.join(folder, file_name)), resolve=False)['core_lib']

    def test_declining_everything_writes_an_empty_library(self):
        # Run as a script: name [Enter = MyCoreLib], cache? no, database? no, job? [no], setup.py? no
        _, folder = self._answer(
            '', 'no', 'no', '', 'no', python_args=('-m', 'core_lib_generator.core_lib_config_generate_yaml')
        )

        self.assertEqual(['MyCoreLib.yaml'], os.listdir(folder))
        self.assertEqual({
            'name': 'MyCoreLib',
            'env': {},
            'connections': [],
            'caches': [],
            'jobs': [],
            'entities': [],
            'data_accesses': [],
            'services': [],
            'setup': {},
        }, self._load(folder, 'MyCoreLib.yaml'))

    def test_every_answer_reaches_the_yaml(self):
        output, folder = self._answer(
            'acme widgets', 'yes',
            'acme_cache', '', 'yes', 'sessions', '3', '', '', '', 'no',     # a memory cache and a Redis cache
            'yes',                                                          # database
            'acme_db', '2', '', '', '', '', '', '', 'db.acme.example', 'reviewer', 's3cret', 'no',
            '', '1', 'widget', '', 'name', '', '', '', 'no', 'yes', 'no', 'no',   # entity: soft delete, no token
            '', '1', '', '', 'get_by_name', 'no', 'yes', 'no',             # its DataAccess, with CRUD soft delete
            '', '1', 'WidgetService', '', 'get_by_name', 'yes', 'yes', 'CACHE_WIDGET', '', 'no', 'no',
            'yes', 'CleanupWidgets', '1h', '24h', 'no',                     # a job
            '', 'acme', 'dev@acme.example', '', 'Widgets for acme', '', '', '1', 'no',   # setup.py
        )

        self.assertTrue(output.endswith(': AcmeWidgets.yaml\n'), output[-200:])   # printed after the last prompt
        self.assertEqual(['AcmeWidgets.yaml'], os.listdir(folder))
        core_lib = self._load(folder, 'AcmeWidgets.yaml')
        self.assertEqual('AcmeWidgets', core_lib['name'])
        # The env variables of every cache and connection, in one place; the caches keep only their own settings.
        self.assertEqual({
            'SESSIONS_PORT': 6379,
            'SESSIONS_HOST': 'localhost',
            'ACME_DB_DB': 'acme_db',
            'ACME_DB_USER': 'reviewer',
            'ACME_DB_PASSWORD': 's3cret',
            'ACME_DB_PORT': 5432,
            'ACME_DB_HOST': 'db.acme.example',
        }, core_lib['env'])
        self.assertEqual([
            {'key': 'acme_cache', 'type': 'memory'},
            {'key': 'sessions', 'type': 'redis',
             'url': {'host': '${oc.env:SESSIONS_HOST}', 'port': '${oc.env:SESSIONS_PORT}', 'protocol': 'redis'}},
        ], core_lib['caches'])
        self.assertEqual([{
            'type': SQL_FACTORY,
            'key': 'acme_db',
            'migrate': False,
            'log_queries': False,
            'create_db': True,
            'session': {'pool_recycle': 3200, 'pool_pre_ping': False},
            'url': {
                'file': '${oc.env:ACME_DB_DB}',
                'protocol': 'postgresql',
                'username': '${oc.env:ACME_DB_USER}',
                'password': '${oc.env:ACME_DB_PASSWORD}',
                'port': '${oc.env:ACME_DB_PORT}',
                'host': '${oc.env:ACME_DB_HOST}',
            },
        }], core_lib['connections'])
        self.assertEqual(['widget'], [entity['key'] for entity in core_lib['entities']])
        self.assertEqual(
            [{'key': 'name', 'type': 'VARCHAR', 'default': None, 'nullable': False}],
            core_lib['entities'][0]['columns'],
        )
        self.assertEqual((True, False), (
            core_lib['entities'][0]['is_soft_delete'], core_lib['entities'][0]['is_soft_delete_token'],
        ))
        data_access = core_lib['data_accesses'][0]
        self.assertEqual(1, len(core_lib['data_accesses']))
        self.assertEqual(
            ('WidgetDataAccess', 'widget', [{'key': 'get_by_name'}], True, True),
            (data_access['key'], data_access['entity'], data_access['functions'], data_access['is_crud'],
             data_access['is_crud_soft_delete']),
        )
        self.assertNotIn('is_crud_soft_delete_token', data_access)
        # A cache exists, so the service was asked whether to cache its function.
        self.assertEqual([{
            'key': 'WidgetService',
            'data_access': 'WidgetDataAccess',
            'functions': [
                {'key': 'get_by_name', 'result_to_dict': True, 'cache_key': 'CACHE_WIDGET', 'cache_invalidate': False},
            ],
        }], core_lib['services'])
        self.assertEqual(
            [('cleanup_widgets', '1h', '24h')],
            [(job['key'], job['initial_delay'], job['frequency']) for job in core_lib['jobs']],
        )
        self.assertEqual({
            'author': 'acme',
            'author_email': 'dev@acme.example',
            'description': 'Widgets for acme',
            'url': '',
            'license': 'MIT',
            'classifiers': ['Development Status :: 3 - Alpha'],
            'version': '0.0.0.1',
        }, core_lib['setup'])

    def test_declining_a_layer_leaves_it_and_every_layer_above_it_empty(self):
        entity = ('1', 'widget', 'no', '', '')    # connection 1, no columns, no soft delete, no other entity
        data_access = ('1', '', 'no', '', 'no')   # entity 1, default name, no functions, no CRUD, no other
        cases = {
            'no entities': (('no',), ([], [], [])),
            'no data access': (('yes', *entity, 'no'), (['widget'], [], [])),
            'no service': (('yes', *entity, 'yes', *data_access, 'no'), (['widget'], ['WidgetDataAccess'], [])),
        }
        for case, (answers, expected) in cases.items():
            with self.subTest(case):
                # name, no cache, a SQLite database, the case's answers, job? [no], setup.py? no
                _, folder = self._answer('acme', 'no', 'yes', *SQLITE_CONNECTION, *answers, '', 'no')

                core_lib = self._load(folder, 'Acme.yaml')
                self.assertEqual(['acme_db'], [connection['key'] for connection in core_lib['connections']])
                self.assertEqual(expected, (
                    [item['key'] for item in core_lib['entities']],
                    [item['key'] for item in core_lib['data_accesses']],
                    [item['key'] for item in core_lib['services']],
                ))
