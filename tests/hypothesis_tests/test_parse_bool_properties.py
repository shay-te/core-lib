"""Property-based tests for parse_utils.parse_bool."""
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import parse_bool
from tests.hypothesis_tests._settings import SETTINGS


class TestParseBoolProperties(unittest.TestCase):
    @given(st.booleans())
    @SETTINGS
    def test_bool_passthrough(self, b):
        self.assertEqual(parse_bool(b), b)

    @given(st.sampled_from(['yes', 'YES', 'true', 'TRUE', 'True', '1']))
    @SETTINGS
    def test_truthy_strings_return_true(self, s):
        self.assertTrue(parse_bool(s))

    @given(st.sampled_from(['no', 'NO', 'false', 'FALSE', 'False', '0']))
    @SETTINGS
    def test_falsy_strings_return_false(self, s):
        self.assertFalse(parse_bool(s))

    @given(st.integers(min_value=-1000, max_value=1000))
    @SETTINGS
    def test_integers_only_0_and_1_parse(self, i):
        result = parse_bool(i)
        if i == 1:
            self.assertTrue(result)
        elif i == 0:
            self.assertFalse(result)
        else:
            self.assertIsNone(result)

    @given(st.floats(allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_floats_return_none(self, f):
        self.assertIsNone(parse_bool(f))
