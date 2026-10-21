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


class TestCommandLineGenerate(unittest.TestCase):

    def tearDown(self):
        GlobalHydra.instance().clear()

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
