"""Property-based tests for parse_utils.parse_any_nan."""
import math
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import parse_any_nan
from tests.hypothesis_tests._settings import SETTINGS


class TestParseAnyNanProperties(unittest.TestCase):
    @given(st.floats(allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_finite_floats_passthrough(self, f):
        # `pd.isna(finite)` is False, so result is the input unchanged
        self.assertEqual(parse_any_nan(f), f)

    @given(st.integers())
    @SETTINGS
    def test_integers_passthrough(self, n):
        self.assertEqual(parse_any_nan(n), n)

    @given(st.text(min_size=1, max_size=10))
    @SETTINGS
    def test_unmatched_strings_passthrough(self, s):
        # No strings_to_replace → strings are passed through unchanged
        self.assertEqual(parse_any_nan(s), s)

    def test_nan_replaced_with_none(self):
        # NaN handling — single value test (hypothesis nan is filtered out above)
        self.assertIsNone(parse_any_nan(float('nan')))

    @given(
        replace=st.text(min_size=1, max_size=5),
    )
    @SETTINGS
    def test_nan_replaced_with_custom(self, replace):
        self.assertEqual(parse_any_nan(float('nan'), replace_with=replace), replace)

    @given(
        items=st.lists(
            st.one_of(
                st.integers(),
                st.text(min_size=1, max_size=5),
            ),
            max_size=10,
        )
    )
    @SETTINGS
    def test_list_preserves_length(self, items):
        result = parse_any_nan(items)
        self.assertEqual(len(result), len(items))
