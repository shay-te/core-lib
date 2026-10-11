"""core-lib's shared SQLAlchemy Base imports without a SQLAlchemy 2.0 deprecation warning."""
import subprocess
import sys
import unittest


class TestSqlalchemyBase(unittest.TestCase):

    def test_base_imports_without_a_deprecation_warning(self):
        # A fresh interpreter: the module is already imported in this one.
        result = subprocess.run(
            [sys.executable, '-W', 'error::DeprecationWarning', '-c',
             'import core_lib.data_layers.data.db.sqlalchemy.base'],
            capture_output=True, text=True, timeout=60,
        )

        self.assertEqual(0, result.returncode, result.stderr)
