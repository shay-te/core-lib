"""setup.py installs core_lib but not core-lib's own `tests` or `examples` packages, which would shadow a user's."""
import os
import runpy
import unittest

import setuptools

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_arguments() -> dict:
    # Run setup.py as pip would, but capture what it passes to setuptools.setup() instead of building.
    captured = {}
    original_setup = setuptools.setup
    original_cwd = os.getcwd()
    setuptools.setup = lambda **kwargs: captured.update(kwargs)
    try:
        os.chdir(REPO_ROOT)
        runpy.run_path(os.path.join(REPO_ROOT, 'setup.py'), run_name='__main__')
    finally:
        setuptools.setup = original_setup
        os.chdir(original_cwd)
    return captured


class TestSetupPackages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.packages = setup_arguments()['packages']

    def test_repository_folders_are_not_installed_as_packages(self):
        # `bin` holds the core_lib script, which setup() installs as a script, not as a package.
        for folder in ('tests', 'examples', 'bin'):
            installed = [package for package in self.packages if package == folder or package.startswith(f'{folder}.')]
            self.assertEqual([], installed, folder)

    def test_library_packages_are_installed(self):
        for package in ('core_lib', 'core_lib.cache', 'core_lib.session', 'core_lib_generator', 'hydra_plugins.core_lib'):
            self.assertIn(package, self.packages)
