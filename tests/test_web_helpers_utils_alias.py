"""The misspelled `web_helprs_utils` still imports, warns, and is the very module `web_helpers_utils` is."""
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_NAME = 'web_helprs_utils'
ALIAS_FILE = os.path.join(REPO_ROOT, 'core_lib', 'web_helpers', f'{OLD_NAME}.py')


def run_python(script: str) -> subprocess.CompletedProcess:
    # A fresh interpreter: an import, and its warning, happen once per process.
    environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
    return subprocess.run([sys.executable, '-c', script], env=environment, capture_output=True, text=True, timeout=60)


class TestWebHelpersUtilsAlias(unittest.TestCase):

    def test_old_name_is_the_new_module_and_warns(self):
        result = run_python(
            'import warnings\n'
            'with warnings.catch_warnings(record=True) as caught:\n'
            '    warnings.simplefilter("always")\n'
            '    from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils as OldWebHelpersUtils\n'
            '    from core_lib.web_helpers import web_helprs_utils as old_module\n'
            'from core_lib.web_helpers import web_helpers_utils as new_module\n'
            'print(old_module is new_module, OldWebHelpersUtils is new_module.WebHelpersUtils)\n'
            'print([str(warning.message) for warning in caught if warning.category is DeprecationWarning])\n'
        )

        self.assertEqual(0, result.returncode, result.stderr)
        identity_line, warnings_line = result.stdout.strip().splitlines()
        self.assertEqual('True True', identity_line)
        self.assertEqual(
            "['`core_lib.web_helpers.web_helprs_utils` is deprecated, "
            "import `core_lib.web_helpers.web_helpers_utils` instead']",
            warnings_line,
        )

    def test_init_through_the_old_name_is_seen_by_the_helpers(self):
        result = run_python(
            'import warnings\n'
            'warnings.simplefilter("ignore", DeprecationWarning)\n'
            'from flask import Flask\n'
            'from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils\n'
            'from core_lib.web_helpers.request_response_helpers import response_status\n'
            'WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)\n'
            'with Flask("acme").app_context():\n'
            '    response = response_status(201)\n'
            'print(type(response).__module__.split(".")[0], response.status_code)\n'
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('flask 201', result.stdout.strip())

    def test_library_code_uses_only_the_new_name(self):
        this_file = os.path.abspath(__file__)
        offenders = []
        for package in ('core_lib', 'core_lib_generator', 'tests', 'examples'):
            for folder, _, file_names in os.walk(os.path.join(REPO_ROOT, package)):
                for file_name in file_names:
                    path = os.path.join(folder, file_name)
                    if not file_name.endswith('.py') or path in (ALIAS_FILE, this_file):
                        continue
                    with open(path) as source_file:
                        if OLD_NAME in source_file.read():
                            offenders.append(os.path.relpath(path, REPO_ROOT))

        self.assertEqual([], offenders)
