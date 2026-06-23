"""Property-based tests for parse_utils.parse_range."""
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import parse_range
from tests.hypothesis_tests._settings import SETTINGS


class TestParseRangeProperties(unittest.TestCase):
    @given(
        st.integers(min_value=0, max_value=10000),
        st.integers(min_value=0, max_value=10000),
    )
    @SETTINGS
    def test_numeric_pair_returns_tuple(self, low, high):
        s = f'{low} to {high}'
        result = parse_range(s)
        self.assertEqual(result, (low, high))

    @given(st.integers(min_value=0, max_value=1000))
    @SETTINGS
    def test_any_min_returns_min_limit(self, hi):
        result = parse_range(f'any to {hi}', min_limit=-9999)
        self.assertEqual(result, (-9999, hi))

    @given(st.integers(min_value=0, max_value=1000))
    @SETTINGS
    def test_any_max_returns_max_limit(self, lo):
        result = parse_range(f'{lo} to any', max_limit=99999)
        self.assertEqual(result, (lo, 99999))
