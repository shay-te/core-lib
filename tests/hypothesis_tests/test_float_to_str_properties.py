"""Property-based tests for parse_utils.float_to_str."""
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import float_to_str
from tests.hypothesis_tests._settings import SETTINGS


class TestFloatToStrProperties(unittest.TestCase):
    @given(st.integers(min_value=-1000000, max_value=1000000))
    @SETTINGS
    def test_int_valued_float_no_dot(self, n):
        self.assertEqual(float_to_str(float(n)), str(n))

    @given(st.floats(allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_finite_float_never_empty_unless_int_zero(self, f):
        result = float_to_str(f)
        if f == 0.0:
            self.assertIn(result, ('0', '-0'))
        else:
            self.assertNotEqual(result, '')

    @given(st.integers(min_value=-100, max_value=100))
    @SETTINGS
    def test_remove_dot_strips_dot_for_non_integer(self, n):
        # n.5 is a non-integer float that has a dot
        value = n + 0.5
        result = float_to_str(value, remove_dot=True)
        self.assertNotIn('.', result)
