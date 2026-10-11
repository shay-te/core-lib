"""setup.py works in an isolated build: it imports neither pip nor core_lib and reads both as text."""
import json
import os
import subprocess
import sys
import unittest

import core_lib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# An isolated (PEP 517) build has setuptools only: `import pip...` and `import core_lib` must fail.
CAPTURE_SETUP_ARGUMENTS = '''
import json, runpy, sys
import setuptools
sys.modules['pip'] = None
sys.modules['core_lib'] = None
captured = {}
setuptools.setup = lambda **kwargs: captured.update(kwargs)
runpy.run_path('setup.py', run_name='__main__')
print(json.dumps({key: captured[key] for key in ('version', 'install_requires', 'long_description')}))
'''

# pip's own requirements parser, the independent oracle. Run apart: pip imports distutils, which must
# never load before setuptools in the test process.
PIP_PARSED_REQUIREMENTS = '''
import json
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
print(json.dumps([str(item.requirement) for item in parse_requirements('requirements.txt', session=PipSession())]))
'''


def run_in_repo(script: str):
    result = subprocess.run([sys.executable, '-c', script], cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class TestSetupIsolatedBuild(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup_arguments = run_in_repo(CAPTURE_SETUP_ARGUMENTS)

    def test_version_is_the_package_version(self):
        self.assertEqual(core_lib.__version__, self.setup_arguments['version'])

    def test_requirements_match_what_pip_parses(self):
        self.assertEqual(run_in_repo(PIP_PARSED_REQUIREMENTS), self.setup_arguments['install_requires'])
        self.assertIn('hydra-core==1.3.6', self.setup_arguments['install_requires'])

    def test_long_description_is_the_readme(self):
        with open(os.path.join(REPO_ROOT, 'README.md')) as readme:
            self.assertEqual(readme.read(), self.setup_arguments['long_description'])
