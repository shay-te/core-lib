"""`core_lib generate --yaml` accepts a YAML path relative to the working directory."""
import os
import shutil
import unittest

from click.testing import CliRunner
from hydra.core.global_hydra import GlobalHydra

from core_lib.core_lib_main import main

EXAMPLE_YAML = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core_lib_generator', 'ExampleCoreLib.yaml'
)
GENERATED_MAIN_CLASS = os.path.join('example_core_lib', 'example_core_lib', 'example_core_lib.py')


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

    def test_absolute_yaml_path_generates_the_project(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            shutil.copy(EXAMPLE_YAML, '.')

            result = runner.invoke(main, ['generate', '--yaml', os.path.abspath('ExampleCoreLib.yaml')])

            self.assertIsNone(result.exception, result.output)
            self.assertTrue(os.path.isfile(GENERATED_MAIN_CLASS))

    def test_missing_yaml_generates_nothing(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ['generate', '--yaml', 'missing.yaml'])

            self.assertIn('yaml file was not found', result.output)
            self.assertEqual([], os.listdir('.'))
