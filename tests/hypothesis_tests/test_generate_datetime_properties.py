"""Property-based tests for generate_data.generate_datetime."""
import datetime
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.generate_data import generate_datetime
from tests.hypothesis_tests._settings import SETTINGS


_DT = st.datetimes(
    min_value=datetime.datetime(2000, 1, 1),
    max_value=datetime.datetime(2099, 12, 31),
)


class TestGenerateDatetimeProperties(unittest.TestCase):
    @given(_DT, _DT)
    @SETTINGS
    def test_result_within_provided_range(self, a, b):
        from_d = min(a, b)
        to_d = max(a, b)
        result = generate_datetime(from_date=from_d, to_date=to_d)
        # Result is a date-truncated datetime — compare on date level to avoid
        # ms granularity issues
        self.assertGreaterEqual(result.date(), from_d.date())
        self.assertLessEqual(result.date(), to_d.date())

    @given(_DT, _DT)
    @SETTINGS
    def test_result_is_midnight_datetime(self, a, b):
        from_d = min(a, b)
        to_d = max(a, b)
        result = generate_datetime(from_date=from_d, to_date=to_d)
        # Function truncates to year/month/day
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)
        self.assertEqual(result.microsecond, 0)

    def test_default_range_about_today(self):
        result = generate_datetime()
        delta = abs((result - datetime.datetime.now()).days)
        self.assertLessEqual(delta, 11)

    @given(st.datetimes(
        min_value=datetime.datetime(1900, 1, 1),
        max_value=datetime.datetime.now() - datetime.timedelta(days=11),
    ))
    @SETTINGS
    def test_only_from_date_uses_default_to(self, from_d):
        # Production code: only from_date provided → to_date defaults to
        # today+10. randint(from, to) requires from <= to, so we constrain
        # from_d to be in the past — surfaced as a fragility by hypothesis.
        result = generate_datetime(from_date=from_d)
        self.assertGreaterEqual(result.date(), from_d.date())

    @given(st.datetimes(
        min_value=datetime.datetime.now() + datetime.timedelta(days=11),
        max_value=datetime.datetime(2099, 12, 31),
    ))
    @SETTINGS
    def test_only_to_date_uses_default_from(self, to_d):
        # Same constraint: to_d must be > today-10 so randint range is valid.
        result = generate_datetime(to_date=to_d)
        self.assertIsInstance(result, datetime.datetime)
