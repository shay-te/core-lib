"""Property-based tests for parse_utils.height_to_cm."""
import math
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import height_to_cm
from tests.hypothesis_tests._settings import SETTINGS


class TestHeightToCmProperties(unittest.TestCase):
    @given(st.integers(min_value=3, max_value=300))
    @SETTINGS
    def test_int_3_or_more_passthrough(self, n):
        # >= 3 means cm — returns the value unchanged
        self.assertEqual(height_to_cm(n), n)

    @given(st.floats(min_value=0.01, max_value=2.99, allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_meters_under_3_converted_to_cm(self, m):
        # < 3 means meters → multiply by 100 and round
        self.assertEqual(height_to_cm(m), round(m * 100))

    @given(st.floats(min_value=3.0, max_value=300.0, allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_floats_3_or_more_are_cm(self, val):
        self.assertEqual(height_to_cm(val), round(val))

    @given(st.integers(min_value=100, max_value=250))
    @SETTINGS
    def test_cm_string_roundtrip(self, n):
        # "180 cm" → 180
        self.assertEqual(height_to_cm(f'{n} cm'), n)
        self.assertEqual(height_to_cm(f'{n}cm'), n)

    @given(st.integers(min_value=1, max_value=2))
    @SETTINGS
    def test_meter_string(self, m):
        # "1m" or "2m" → m * 100
        self.assertEqual(height_to_cm(f'{m} m'), m * 100)

    @given(st.one_of(
        st.lists(st.integers()),
        st.dictionaries(st.text(), st.integers()),
        st.tuples(st.integers()),
        st.sets(st.integers()),
    ))
    @SETTINGS
    def test_collections_return_none(self, collection):
        self.assertIsNone(height_to_cm(collection))

    def test_nan_returns_none(self):
        self.assertIsNone(height_to_cm(float('nan')))

    def test_inf_returns_none(self):
        self.assertIsNone(height_to_cm(float('inf')))

    @given(st.text(min_size=1, max_size=10).filter(
        lambda s: not any(c.isdigit() for c in s)
    ))
    @SETTINGS
    def test_pure_non_numeric_strings_return_none(self, s):
        # Strings without any digits cannot match any height pattern
        self.assertIsNone(height_to_cm(s))
