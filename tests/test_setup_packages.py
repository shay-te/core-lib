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

    def test_tests_package_is_not_installed(self):
        packages = setup_arguments()['packages']

        test_packages = [package for package in packages if package == 'tests' or package.startswith('tests.')]
        self.assertEqual([], test_packages)

    def test_examples_package_is_not_installed(self):
        packages = setup_arguments()['packages']

        example_packages = [package for package in packages if package == 'examples' or package.startswith('examples.')]
        self.assertEqual([], example_packages)

    def test_library_packages_are_installed(self):
        packages = setup_arguments()['packages']

        for package in ('core_lib', 'core_lib.cache', 'core_lib.session', 'core_lib_generator', 'hydra_plugins.core_lib'):
            self.assertIn(package, packages)
