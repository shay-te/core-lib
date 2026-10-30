"""setup.py works in an isolated build: it imports neither pip nor core_lib and reads both as text."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import core_lib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# An isolated (PEP 517) build has setuptools only: `import pip...` and `import core_lib` must fail.
# Run from another folder, so setup.py must find its files next to itself, not in the working directory.
CAPTURE_SETUP_ARGUMENTS = f'''
import json, runpy, sys
import setuptools
sys.modules['pip'] = None
sys.modules['core_lib'] = None
captured = {{}}
setuptools.setup = lambda **kwargs: captured.update(kwargs)
runpy.run_path({os.path.join(REPO_ROOT, 'setup.py')!r}, run_name='__main__')
print(json.dumps({{key: captured[key] for key in ('version', 'install_requires', 'long_description')}}))
'''

# pip's own requirements parser, the independent oracle. Run apart: pip imports distutils, which must
# never load before setuptools in the test process.
PIP_PARSED_REQUIREMENTS = '''
import json
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
print(json.dumps([str(item.requirement) for item in parse_requirements('requirements.txt', session=PipSession())]))
'''


def run_python(script: str, folder: str):
    result = subprocess.run([sys.executable, '-c', script], cwd=folder, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class TestSetupIsolatedBuild(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        other_folder = tempfile.mkdtemp()
        try:
            cls.setup_arguments = run_python(CAPTURE_SETUP_ARGUMENTS, other_folder)
        finally:
            shutil.rmtree(other_folder)

    def test_version_is_the_package_version(self):
        self.assertEqual(core_lib.__version__, self.setup_arguments['version'])

    def test_requirements_match_what_pip_parses(self):
        self.assertEqual(run_python(PIP_PARSED_REQUIREMENTS, REPO_ROOT), self.setup_arguments['install_requires'])

    def test_long_description_is_the_readme(self):
        with open(os.path.join(REPO_ROOT, 'README.md')) as readme:
            self.assertEqual(readme.read(), self.setup_arguments['long_description'])
