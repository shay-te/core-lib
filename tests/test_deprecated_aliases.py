"""Every renamed module or class keeps its old name until 1.0.0: it still works, gives the very same object, and warns
with both versions. Library code uses only the new names, and every old name is gone by 1.0.0."""
import os
import re
import subprocess
import sys
import unittest

import core_lib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOVED_IN = (1, 0)
CONNECTION = os.path.join(REPO_ROOT, 'core_lib', 'connection')

# (old import, new import, the deprecation message, the alias's source file)
ALIASES = [
    (
        'from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils',
        'from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils',
        '`core_lib.web_helpers.web_helprs_utils` is deprecated since 0.3.0 and will be removed in 1.0.0, '
        'import `core_lib.web_helpers.web_helpers_utils` instead',
        os.path.join(REPO_ROOT, 'core_lib', 'web_helpers', 'web_helprs_utils.py'),
    ),
    (
        'from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess',
        'from core_lib.data_layers.data_access.db.crud.crud_soft_delete_data_access import CRUDSoftDeleteDataAccess',
        '`core_lib.data_layers.data_access.db.crud.crud_soft_data_access` is deprecated since 0.3.0 and will be '
        'removed in 1.0.0, import `core_lib.data_layers.data_access.db.crud.crud_soft_delete_data_access` instead',
        os.path.join(REPO_ROOT, 'core_lib', 'data_layers', 'data_access', 'db', 'crud', 'crud_soft_data_access.py'),
    ),
    (
        'from core_lib.connection.elasticsearch_connection import ElasticSearchConnection',
        'from core_lib.connection.elasticsearch_connection import ElasticsearchConnection',
        '`ElasticSearchConnection` is deprecated since 0.3.0 and will be removed in 1.0.0, '
        'use `ElasticsearchConnection` instead',
        os.path.join(CONNECTION, 'elasticsearch_connection.py'),
    ),
    (
        'from core_lib.connection.elasticsearch_connection_factory import ElasticSearchConnectionFactory',
        'from core_lib.connection.elasticsearch_connection_factory import ElasticsearchConnectionFactory',
        '`ElasticSearchConnectionFactory` is deprecated since 0.3.0 and will be removed in 1.0.0, '
        'use `ElasticsearchConnectionFactory` instead',
        os.path.join(CONNECTION, 'elasticsearch_connection_factory.py'),
    ),
]
# How each old name is spelled where it is used.
OLD_NAMES = re.compile(
    r'web_helprs_utils|crud_soft_data_access|ElasticSearchConnection'
)


def imported_names(import_line: str) -> list:
    return [name.strip() for name in import_line.split(' import ')[1].split(',')]


class TestDeprecatedAliases(unittest.TestCase):

    def test_old_names_give_the_same_object_and_warn(self):
        for old_import, new_import, message, _ in ALIASES:
            names = imported_names(old_import)
            # A fresh interpreter for each: an import, and its warning, happen once per process.
            script = (
                'import warnings\n'
                'with warnings.catch_warnings(record=True) as caught:\n'
                '    warnings.simplefilter("always")\n'
                f'    {old_import}\n'
                f'    old = ({", ".join(names)},)\n'
                f'{new_import}\n'
                f'new = ({", ".join(names)},)\n'
                'print(all(left is right for left, right in zip(old, new)))\n'
                'print([str(warning.message) for warning in caught if warning.category is DeprecationWarning])\n'
            )
            environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
            with self.subTest(old_import):
                result = subprocess.run(
                    [sys.executable, '-c', script], env=environment, capture_output=True, text=True, timeout=60
                )

                self.assertEqual(0, result.returncode, result.stderr)
                identity_line, warnings_line = result.stdout.strip().splitlines()
                self.assertEqual('True', identity_line)
                self.assertEqual(repr([message]), warnings_line)

    def test_library_code_uses_only_the_new_names(self):
        alias_files = {alias_file for *_, alias_file in ALIASES if not alias_file.startswith(CONNECTION)}
        offenders = []
        for package in ('core_lib', 'core_lib_generator', 'tests', 'examples', 'website'):
            for folder, _, file_names in os.walk(os.path.join(REPO_ROOT, package)):
                for file_name in file_names:
                    path = os.path.join(folder, file_name)
                    if not file_name.endswith('.py') or path in alias_files or path == os.path.abspath(__file__):
                        continue
                    with open(path, encoding='utf-8') as source_file:
                        source = source_file.read()
                    if path.startswith(CONNECTION):
                        source = source.split('def __getattr__(name):')[0]   # the old class name lives in the hook
                    if OLD_NAMES.search(source):
                        offenders.append(os.path.relpath(path, REPO_ROOT))

        self.assertEqual([], offenders)

    def test_old_names_are_gone_by_their_removal_version(self):
        # Every warning promises removal in 1.0.0: releasing 1.0.0 with an old name still here breaks that promise.
        version = tuple(int(part) for part in core_lib.__version__.split('.')[:2])
        if version >= REMOVED_IN:
            for old_import, _, _, alias_file in ALIASES:
                with self.subTest(old_import):
                    if alias_file.startswith(CONNECTION):
                        with open(alias_file, encoding='utf-8') as source_file:
                            self.assertNotIn('def __getattr__(name):', source_file.read())
                    else:
                        self.assertFalse(os.path.exists(alias_file), f'{old_import} was due for removal in 1.0.0')
