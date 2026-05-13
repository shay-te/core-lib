"""Property-based tests for validation.parse_int_list."""
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.validation import parse_int_list
from tests.hypothesis_tests._settings import SETTINGS


class TestParseIntListProperties(unittest.TestCase):
    @given(st.lists(st.integers(min_value=-1000000, max_value=1000000), max_size=30))
    @SETTINGS
    def test_roundtrip(self, nums):
        s = ','.join(str(n) for n in nums)
        self.assertEqual(parse_int_list(s), nums)

    @given(st.lists(st.integers(), min_size=1, max_size=30))
    @SETTINGS
    def test_with_spaces_around_separators(self, nums):
        s = ', '.join(str(n) for n in nums)
        self.assertEqual(parse_int_list(s), nums)

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(parse_int_list(''), [])

    def test_none_returns_empty_list(self):
        self.assertEqual(parse_int_list(None), [])

    @given(st.lists(st.integers(), min_size=1, max_size=10))
    @SETTINGS
    def test_extra_empty_segments_ignored(self, nums):
        s = ',,'.join(str(n) for n in nums)
        # Doubled commas create empty segments that should be filtered
        self.assertEqual(parse_int_list(s), nums)
