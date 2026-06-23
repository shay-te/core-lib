"""Property-based tests for parse_utils.parse_date."""
import datetime
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import parse_date
from tests.hypothesis_tests._settings import SETTINGS


_VALID_DATES = st.dates(
    min_value=datetime.date(1970, 1, 1),
    max_value=datetime.date(2099, 12, 31),
)


class TestParseDateProperties(unittest.TestCase):
    @given(_VALID_DATES)
    @SETTINGS
    def test_iso_dash_format_roundtrip(self, d):
        # 2024-06-15 → datetime(2024, 6, 15)
        result = parse_date(d.strftime('%Y-%m-%d'))
        self.assertEqual(result, datetime.datetime(d.year, d.month, d.day))

    @given(_VALID_DATES)
    @SETTINGS
    def test_iso_slash_format_roundtrip(self, d):
        # 2024/06/15 → datetime(2024, 6, 15)
        result = parse_date(d.strftime('%Y/%m/%d'))
        self.assertEqual(result, datetime.datetime(d.year, d.month, d.day))

    @given(_VALID_DATES)
    @SETTINGS
    def test_iso_dot_format_roundtrip(self, d):
        result = parse_date(d.strftime('%Y.%m.%d'))
        self.assertEqual(result, datetime.datetime(d.year, d.month, d.day))

    @given(st.datetimes(
        min_value=datetime.datetime(1970, 1, 1),
        max_value=datetime.datetime(2099, 12, 31),
    ))
    @SETTINGS
    def test_datetime_passthrough(self, dt):
        # datetime objects pass through unchanged
        self.assertEqual(parse_date(dt), dt)

    @given(st.floats(allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_numbers_return_none(self, n):
        self.assertIsNone(parse_date(n))

    @given(st.integers())
    @SETTINGS
    def test_integers_return_none(self, n):
        self.assertIsNone(parse_date(n))
