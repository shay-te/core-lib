"""`core_lib generate` builds a project from a YAML path, or from answers typed at its prompts."""
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from click.testing import CliRunner
from hydra.core.global_hydra import GlobalHydra

from core_lib.core_lib_main import main

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE_YAML = os.path.join(REPO_ROOT, 'core_lib_generator', 'ExampleCoreLib.yaml')
CORE_LIB_COMMAND = os.path.join(REPO_ROOT, 'bin', 'core_lib')
GENERATED_MAIN_CLASS = os.path.join('example_core_lib', 'example_core_lib', 'example_core_lib.py')
GENERATED_DETAILS_ENTITY = os.path.join(
    'example_core_lib', 'example_core_lib', 'data_layers', 'data', 'sqlconn', 'entities', 'details.py'
)
GENERATION_PAGE = os.path.join(REPO_ROOT, 'docs', 'pages', 'core_lib_doc', 'Command Line', 'Generation.md')
PROMPTS_PAGE = os.path.join(REPO_ROOT, 'docs', 'pages', 'core_lib_doc', 'Helpers', 'shell_utils.md')
PROMPTS_LIMIT = 'with no database and no jobs'
PROMPTS_FIXED = 'The prompts now handle this library. Drop this case, and the docs warning once no case is left.'
SQLITE_CONNECTION = ('acme_db', '', '', '', '', '', '', '')   # name, then Enter for every SQLite setting and "another?"
SQL_FACTORY = 'core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory'
GENERATE_TIME_VALUE = 'value-from-the-generating-machine'
UNRESOLVED_VALUE = '${oc.env:ACME_GENERATE_VALUE}'
# One interpolation in every place a YAML can hold a plain value.
INTERPOLATED_YAML = f'''
core_lib:
  name: AcmeCoreLib
  env:
    ACME_HOST: {UNRESOLVED_VALUE}
  connections:
    - key: acme_db
      type: {SQL_FACTORY}
      migrate: false
      config:
        log_queries: {UNRESOLVED_VALUE}
        url:
          protocol: {UNRESOLVED_VALUE}
          file: {UNRESOLVED_VALUE}
  caches:
    - key: sessions
      type: redis
      url:
        protocol: redis
        host: {UNRESOLVED_VALUE}
  jobs:
    - key: cleanup
      initial_delay: {UNRESOLVED_VALUE}
      frequency: {UNRESOLVED_VALUE}
      handler:
        _target_: acme_core_lib.jobs.cleanup.Cleanup
  setup:
    author: {UNRESOLVED_VALUE}
    author_email: {UNRESOLVED_VALUE}
    description: {UNRESOLVED_VALUE}
    url: {UNRESOLVED_VALUE}
    license: MIT
    classifiers: []
    version: 0.0.0.1
'''
BUILD_GENERATED_LIBRARY = (
    'from tests.test_data.helpers.util import load_config\n'
    'from acme.acme import Acme\n'
    'Acme(load_config())\n'
)


class TestCommandLineGenerate(unittest.TestCase):

    def tearDown(self):
        GlobalHydra.instance().clear()

    def _generate_from_answers(self, *answers) -> tuple:
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        generated = subprocess.run(
            [sys.executable, CORE_LIB_COMMAND, 'generate'], input=''.join(f'{line}\n' for line in answers),
            cwd=folder, env=dict(os.environ, PYTHONPATH=REPO_ROOT), capture_output=True, text=True, timeout=120,
        )
        return generated, os.path.join(folder, 'acme')

    def _build(self, project_root: str):
        return subprocess.run(
            [sys.executable, '-c', BUILD_GENERATED_LIBRARY], cwd=project_root, capture_output=True, text=True,
            timeout=120, env=dict(os.environ, PYTHONPATH=os.pathsep.join([project_root, REPO_ROOT])),
        )

    def test_relative_yaml_path_generates_the_project(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('specs')
            shutil.copy(EXAMPLE_YAML, 'specs')

            result = runner.invoke(main, ['generate', '--yaml', os.path.join('specs', 'ExampleCoreLib.yaml')])

            self.assertIsNone(result.exception, result.output)
            self.assertEqual(0, result.exit_code)
            self.assertTrue(os.path.isfile(GENERATED_MAIN_CLASS))
            with open(GENERATED_DETAILS_ENTITY) as entity:
                # The sample's INTEGER column has no default: an empty string would be written as one.
                self.assertIn('    contact = Column(INTEGER, nullable=None, default=None)\n', entity.read())

    def test_missing_yaml_is_reported_and_nothing_is_generated(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        missing_path = os.path.join(folder, 'specs', 'AcmeCoreLib.yaml')

        result = CliRunner().invoke(main, ['generate', '--yaml', missing_path])

        self.assertIn('yaml file was not found', result.output)
        self.assertIn(f'path:{missing_path}', result.output)
        # It stops at the message (an exit is not an Exception), with a status a script can test.
        self.assertNotIsInstance(result.exception, Exception)
        self.assertEqual(1, result.exit_code)
        self.assertEqual([], os.listdir(folder))

    def test_no_value_in_the_yaml_is_resolved(self):
        for environment_value in (None, GENERATE_TIME_VALUE):
            folder = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, folder)
            with open(os.path.join(folder, 'acme.yaml'), 'w') as yaml_file:
                yaml_file.write(INTERPOLATED_YAML)
            environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
            environment.pop('ACME_GENERATE_VALUE', None)
            if environment_value:
                environment['ACME_GENERATE_VALUE'] = environment_value

            generated = subprocess.run(
                [sys.executable, CORE_LIB_COMMAND, 'generate', '--yaml', 'acme.yaml'],
                cwd=folder, env=environment, capture_output=True, text=True, timeout=120,
            )

            self.assertEqual(0, generated.returncode, generated.stderr[-3000:])
            project_root = os.path.join(folder, 'acme_core_lib')
            contents = {}
            for path, _, file_names in os.walk(project_root):
                for file_name in file_names:
                    with open(os.path.join(path, file_name)) as generated_file:
                        contents[os.path.relpath(os.path.join(path, file_name), project_root)] = generated_file.read()
            self.assertEqual([], [name for name, text in contents.items() if GENERATE_TIME_VALUE in text])
            config = contents[os.path.join('acme_core_lib', 'config', 'acme_core_lib.yaml')]
            self.assertEqual(6, config.count(UNRESOLVED_VALUE))   # 3 connection, 1 cache and 2 job values
            self.assertIn(f'ACME_HOST={UNRESOLVED_VALUE}', contents['.env'])
            self.assertIn(f"description='{UNRESOLVED_VALUE}'", contents['setup.py'].replace('"', "'"))

        with open(GENERATION_PAGE, encoding='utf-8') as page:
            self.assertIn('never resolves `${...}` values', page.read())

    def test_the_docs_warn_about_the_libraries_the_prompts_cannot_build(self):
        # The YAML the prompts write does not match what the generator reads. Each case is a known bug, so each states
        # what really happens: fixing one fails here, which is the reminder to take the warning off both pages.
        generated, _ = self._generate_from_answers(
            'acme', 'no', 'yes', *SQLITE_CONNECTION, 'yes', '1', 'widget', 'no', '', '', 'no', '', 'no',
        )
        self.assertNotEqual(0, generated.returncode, PROMPTS_FIXED)    # a database with an entity
        self.assertIn("'connection'", generated.stderr)

        generated, project_root = self._generate_from_answers('acme', 'no', 'yes', *SQLITE_CONNECTION, 'no', '', 'no')
        self.assertEqual(0, generated.returncode, generated.stderr)    # a database without entities
        with open(os.path.join(project_root, 'acme', 'config', 'acme.yaml')) as config_file:
            self.assertIn('acme_db: null', config_file.read(), PROMPTS_FIXED)
        built = self._build(project_root)
        self.assertNotEqual(0, built.returncode, PROMPTS_FIXED)
        self.assertIn("'NoneType' object has no attribute 'get'", built.stderr)

        generated, project_root = self._generate_from_answers(
            'acme', 'no', 'no', 'yes', 'CleanupWidgets', '1h', '24h', 'no', 'no',
        )
        self.assertEqual(0, generated.returncode, generated.stderr)    # a job
        built = self._build(project_root)
        self.assertNotEqual(0, built.returncode, PROMPTS_FIXED)
        self.assertIn('acme.acme.jobs.cleanup_widgets.CleanupWidgets', built.stderr)   # one package too deep

        for page in (GENERATION_PAGE, PROMPTS_PAGE):
            with open(page, encoding='utf-8') as page_file:
                self.assertIn(PROMPTS_LIMIT, page_file.read())

    def test_answers_typed_at_the_prompts_generate_a_project_that_builds(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        answers = (
            'acme widgets',                                   # the library's name, made PascalCase
            'yes', 'widget_cache', '', 'no',                  # one in-memory cache
            'no',                                             # no database
            'no',                                             # no job
            'yes', 'acme', 'dev@acme.example', '', 'Widgets for acme', '', '', '1', 'no',   # setup.py, MIT
        )
        environment = dict(os.environ, PYTHONPATH=REPO_ROOT)

        generated = subprocess.run(
            [sys.executable, CORE_LIB_COMMAND, 'generate'], input=''.join(f'{line}\n' for line in answers),
            cwd=folder, env=environment, capture_output=True, text=True, timeout=120,
        )

        self.assertEqual(0, generated.returncode, generated.stderr)
        # The answers are kept next to the project, so it can be generated again with --yaml.
        self.assertEqual(['AcmeWidgets.yaml', 'acme_widgets'], sorted(os.listdir(folder)))
        project_root = os.path.join(folder, 'acme_widgets')
        today = datetime.datetime.utcnow()
        with open(os.path.join(project_root, f'LICENSE_{today.year}_{today.month}_{today.day}')) as license_file:
            self.assertEqual(['MIT License', '', f'Copyright {today.year} acme'], license_file.read().splitlines()[:3])
        script = (
            'from core_lib.core_lib import CoreLib\n'
            'from tests.test_data.helpers.util import load_config\n'
            'from acme_widgets.acme_widgets import AcmeWidgets\n'
            'config = load_config()\n'
            'AcmeWidgets(config)\n'
            'AcmeWidgets(config)\n'
            'print(CoreLib.cache_registry.registered())\n'
            'print(type(CoreLib.cache_registry.get("widget_cache")).__name__)\n'
        )
        built = subprocess.run(
            [sys.executable, '-c', script], cwd=project_root, capture_output=True, text=True, timeout=120,
            env=dict(os.environ, PYTHONPATH=os.pathsep.join([project_root, REPO_ROOT])),
        )

        self.assertEqual(0, built.returncode, built.stderr)
        self.assertEqual(["['widget_cache']", 'CacheHandlerRam'], built.stdout.splitlines())
