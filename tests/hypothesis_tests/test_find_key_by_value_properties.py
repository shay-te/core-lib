"""Property-based tests for parse_utils.find_key_by_value."""
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import find_key_by_value
from tests.hypothesis_tests._settings import SETTINGS


class TestFindKeyByValueProperties(unittest.TestCase):
    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.integers(min_value=0, max_value=1000),
            min_size=1,
            max_size=20,
        )
    )
    @SETTINGS
    def test_found_value_returns_a_valid_key(self, d):
        target = next(iter(d.values()))
        key = find_key_by_value(d, target)
        self.assertEqual(d[key], target)

    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.integers(min_value=0, max_value=100),
        ),
        st.integers(min_value=99999, max_value=100000),
    )
    @SETTINGS
    def test_missing_value_returns_none(self, d, target):
        # Target outside the value range used to build d
        # (filter ensures we never accidentally land on a match)
        if target not in d.values():
            self.assertIsNone(find_key_by_value(d, target))
