"""A project made by `core_lib generate` builds its CoreLib twice in one process and its own tests pass."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from click.testing import CliRunner
from hydra.core.global_hydra import GlobalHydra

from core_lib.core_lib_main import main

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_YAML = os.path.join(REPO_ROOT, 'tests', 'test_data', 'generator', 'AcmeCoreLib.yaml')


class TestGeneratedProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.output_folder = tempfile.mkdtemp()
        shutil.copy(SAMPLE_YAML, cls.output_folder)
        original_cwd = os.getcwd()
        try:
            os.chdir(cls.output_folder)
            result = CliRunner().invoke(main, ['generate', '--yaml', 'AcmeCoreLib.yaml'])
        finally:
            os.chdir(original_cwd)
            GlobalHydra.instance().clear()
        if result.exception:
            raise result.exception
        cls.project_root = os.path.join(cls.output_folder, 'acme_core_lib')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.output_folder)

    def _run_in_project(self, *args) -> subprocess.CompletedProcess:
        environment = dict(os.environ, PYTHONPATH=os.pathsep.join([REPO_ROOT, self.project_root]))
        return subprocess.run(
            [sys.executable, *args], cwd=self.project_root, env=environment, capture_output=True, text=True, timeout=120
        )

    def _generated_files(self):
        for folder, _, file_names in os.walk(self.project_root):
            for file_name in file_names:
                if file_name.endswith(('.py', '.yaml', '.md', '.txt', '.in')):
                    yield os.path.join(folder, file_name)

    def test_generated_tests_pass(self):
        result = self._run_in_project('-m', 'unittest', 'discover', '-s', 'tests', '-t', '.')

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Ran 1 test', result.stderr)

    def test_core_lib_builds_twice_in_one_process(self):
        script = (
            'from tests.test_data.helpers.util import load_config\n'
            'from acme_core_lib.acme_core_lib import AcmeCoreLib\n'
            'config = load_config()\n'
            'first = AcmeCoreLib(config)\n'
            'second = AcmeCoreLib(config)\n'
            'print(type(second.widget).__name__, type(second.widget._data_access).__name__)\n'
            "print(hasattr(second, 'widget_data_access'), hasattr(second, 'widget_service'))\n"
        )
        result = self._run_in_project('-c', script)

        self.assertEqual(0, result.returncode, result.stderr)
        wiring_line, public_names_line = result.stdout.strip().splitlines()
        # The service is public under its rulebook name and holds a DataAccess instance; the DataAccess is private.
        self.assertEqual('WidgetService WidgetDataAccess', wiring_line)
        self.assertEqual('False False', public_names_line)

    def test_readme_example_runs(self):
        with open(os.path.join(self.project_root, 'README.md')) as readme:
            example = re.search(r'```python\n(.*?)```', readme.read(), flags=re.S).group(1)
        with open(os.path.join(self.project_root, 'readme_example.py'), 'w') as example_file:
            example_file.write(example)

        result = self._run_in_project('readme_example.py')

        self.assertIn('acme_core_lib.widget.get_by_name()', example)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_generated_setup_builds_isolated_and_does_not_install_tests(self):
        # An isolated build has setuptools only: neither pip nor the library itself is importable.
        script = (
            'import runpy, setuptools, sys\n'
            "sys.modules['pip'] = None\n"
            "sys.modules['acme_core_lib'] = None\n"
            'captured = {}\n'
            'setuptools.setup = lambda **kwargs: captured.update(kwargs)\n'
            "runpy.run_path('setup.py', run_name='__main__')\n"
            "print(sorted(captured['packages']))\n"
            "print(captured['python_requires'], captured['version'], captured['install_requires'])\n"
        )
        result = self._run_in_project('-c', script)

        self.assertEqual(0, result.returncode, result.stderr)
        packages_line, settings_line = result.stdout.strip().splitlines()
        self.assertNotIn("'tests", packages_line)
        self.assertIn("'acme_core_lib'", packages_line)
        self.assertIn("'hydra_plugins.acme_core_lib'", packages_line)
        self.assertEqual(">=3.10 0.0.0.1 ['core-lib']", settings_line)

    def test_no_template_placeholder_or_host_name_is_left(self):
        for path in self._generated_files():
            with open(path) as generated_file:
                content = generated_file.read()
            self.assertNotIn('# template_', content, path)
            self.assertNotIn('ob-love', content, path)
