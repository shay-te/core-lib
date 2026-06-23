"""Property-based tests for helpers.validation (is_int, is_float)."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.validation import is_float, is_int
from tests.hypothesis_tests._settings import SETTINGS


class TestValidationProperties(unittest.TestCase):
    @given(st.integers())
    @SETTINGS
    def test_int_objects_are_int(self, n):
        self.assertTrue(is_int(n))

    @given(st.integers())
    @SETTINGS
    def test_int_strings_are_int(self, n):
        self.assertTrue(is_int(str(n)))

    @given(st.floats(allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_floats_are_float(self, f):
        self.assertTrue(is_float(f))

    @given(st.floats(allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_float_strings_are_float(self, f):
        self.assertTrue(is_float(str(f)))

    @given(st.integers())
    @SETTINGS
    def test_int_is_also_float(self, n):
        self.assertTrue(is_float(n))

    @given(
        st.text(alphabet=stringmod.ascii_lowercase, min_size=1).filter(
            lambda s: not any(c.isdigit() for c in s)
        )
    )
    @SETTINGS
    def test_pure_letters_are_not_int(self, s):
        self.assertFalse(is_int(s))
