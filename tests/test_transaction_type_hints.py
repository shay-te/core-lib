"""The transaction classes stay resilient to reflection: every type hint is a real, importable type
(typing.get_type_hints resolves it), every module imports on its own whatever the order, and no module in core_lib
hides an import under typing.TYPE_CHECKING."""
import ast
import inspect
import os
import subprocess
import sys
import typing
import unittest

import core_lib
from core_lib.connection.sql_alchemy_connection import SqlAlchemyConnection
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.connection.transaction_decorator import Transaction
from core_lib.connection.transaction_manager import TransactionManager
from core_lib.connection.transaction_scope_registry import TransactionScopeRegistry
from core_lib.connection.transaction_scope import TransactionScope
from core_lib.connection.transactional_connection import TransactionalConnection
from core_lib.connection.transactional_connection_factory import TransactionalConnectionFactory

TRANSACTION_CLASSES = (Transaction, TransactionScope, TransactionManager, TransactionScopeRegistry,
                       TransactionalConnection, TransactionalConnectionFactory, SqlAlchemyConnection,
                       SqlAlchemyConnectionFactory)
TRANSACTION_MODULES = ('core_lib.connection.transaction_decorator', 'core_lib.connection.transaction_manager',
                       'core_lib.connection.transaction_scope_registry', 'core_lib.connection.transaction_scope',
                       'core_lib.connection.transactional_connection', 'core_lib.connection.transactional_connection_factory',
                       'core_lib.connection.sql_alchemy_connection', 'core_lib.connection.sql_alchemy_connection_factory',
                       'core_lib.cache.cache_decorator', 'core_lib.core_lib')
CORE_LIB_DIRECTORY = os.path.dirname(core_lib.__file__)
REPO_ROOT = os.path.dirname(CORE_LIB_DIRECTORY)
WAIT_SECONDS = 60


def _uses_type_checking(source: str) -> bool:
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and node.id == 'TYPE_CHECKING':
            return True
        if isinstance(node, ast.Attribute) and node.attr == 'TYPE_CHECKING':
            return True
        if isinstance(node, ast.alias) and node.name == 'TYPE_CHECKING':
            return True
    return False


def _functions_of(cls) -> list:
    functions = []
    for name, attribute in vars(cls).items():
        if isinstance(attribute, (staticmethod, classmethod)):
            attribute = attribute.__func__
        if inspect.isfunction(attribute):
            functions.append((name, attribute))
    return functions


class TestTransactionTypeHints(unittest.TestCase):

    def test_every_type_hint_of_the_transaction_classes_resolves(self):
        unresolved = []
        for cls in TRANSACTION_CLASSES:
            for target_name, target in [('<class>', cls)] + _functions_of(cls):
                try:
                    typing.get_type_hints(target)
                except Exception as error:
                    unresolved.append('{}.{}: {}'.format(cls.__name__, target_name, error))

        self.assertEqual([], unresolved)
        self.assertIs(TransactionalConnectionFactory,
                      typing.get_type_hints(TransactionManager.get_connection)['connection_factory'])

    def test_every_transaction_module_imports_first_in_a_fresh_interpreter(self):
        failures = []
        for module in TRANSACTION_MODULES:
            completed = subprocess.run([sys.executable, '-c', 'import {}'.format(module)], cwd=REPO_ROOT,
                                       capture_output=True, text=True, timeout=WAIT_SECONDS)
            if completed.returncode != 0:
                failures.append('{}: {}'.format(module, completed.stderr.strip().splitlines()[-1]))

        self.assertEqual([], failures)

    def test_no_module_in_core_lib_uses_type_checking(self):
        offenders = []
        for directory, _, file_names in os.walk(CORE_LIB_DIRECTORY):
            for file_name in file_names:
                if file_name.endswith('.py'):
                    path = os.path.join(directory, file_name)
                    with open(path, encoding='utf-8') as source:
                        if _uses_type_checking(source.read()):
                            offenders.append(os.path.relpath(path, REPO_ROOT))

        self.assertEqual([], offenders)

    def test_the_type_checking_scan_finds_every_spelling(self):
        # so an empty result above means "none", never "the scan stopped working"
        for planted in ('from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    pass\n',
                        'import typing\nif typing.TYPE_CHECKING:\n    pass\n'):
            self.assertTrue(_uses_type_checking(planted))
        self.assertFalse(_uses_type_checking('import typing\nvalue: typing.Optional[int] = None\n'))
