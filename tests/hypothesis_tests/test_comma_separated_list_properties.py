"""Property-based tests for parse_comma_separated_list round-trips."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.validation import parse_comma_separated_list
from tests.hypothesis_tests._settings import SETTINGS


class TestCommaSeparatedListProperties(unittest.TestCase):
    @given(
        st.lists(
            st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10),
            max_size=20,
        )
    )
    @SETTINGS
    def test_roundtrip_via_join(self, items):
        s = ','.join(items)
        parsed = parse_comma_separated_list(s)
        self.assertEqual(parsed, items)

    @given(st.lists(st.integers(min_value=-1000, max_value=1000), max_size=20))
    @SETTINGS
    def test_int_parser_roundtrip(self, nums):
        s = ','.join(str(n) for n in nums)
        parsed = parse_comma_separated_list(s, value_parser=int)
        self.assertEqual(parsed, nums)
