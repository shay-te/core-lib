"""Property-based tests for helpers.datetime_utils.

These exercise relative invariants — like ``tomorrow > today``,
``week_begin.weekday() == 0``, ``year_begin.month == 1`` — across the
full hours/minutes parameter space.
"""
import datetime
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.datetime_utils import (
    age,
    day_begin,
    day_end,
    friday,
    hour_begin,
    hour_end,
    midnight,
    monday,
    month_begin,
    month_end,
    reset_datetime,
    saturday,
    sunday,
    thursday,
    timestamp_to_ms,
    today,
    tomorrow,
    tuesday,
    wednesday,
    week_begin,
    week_end,
    year_begin,
    year_end,
    yesterday,
)
from tests.hypothesis_tests._settings import SETTINGS


_HOURS = st.integers(min_value=0, max_value=23)
_MINUTES = st.integers(min_value=0, max_value=59)


# ── hour_begin / hour_end ──────────────────────────────────────────────────


class TestHourFunctionsProperties(unittest.TestCase):
    @given(minutes=_MINUTES)
    @SETTINGS
    def test_hour_begin_minute_respected(self, minutes):
        result = hour_begin(minutes=minutes)
        self.assertEqual(result.minute, minutes)
        self.assertEqual(result.second, 0)
        self.assertEqual(result.microsecond, 0)

    @given(minutes=_MINUTES)
    @SETTINGS
    def test_hour_end_is_one_hour_after_begin(self, minutes):
        self.assertEqual(
            hour_end(minutes=minutes) - hour_begin(minutes=minutes),
            datetime.timedelta(hours=1),
        )


# ── day_begin / day_end ────────────────────────────────────────────────────


class TestDayFunctionsProperties(unittest.TestCase):
    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_day_begin_respects_parameters(self, hours, minutes):
        result = day_begin(hours=hours, minutes=minutes)
        self.assertEqual(result.hour, hours)
        self.assertEqual(result.minute, minutes)
        self.assertEqual(result.second, 0)
        self.assertEqual(result.microsecond, 0)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_day_end_is_one_day_after_begin(self, hours, minutes):
        self.assertEqual(
            day_end(hours=hours, minutes=minutes) - day_begin(hours=hours, minutes=minutes),
            datetime.timedelta(days=1),
        )


# ── today / tomorrow / yesterday / midnight ───────────────────────────────


class TestRelativeDayFunctionsProperties(unittest.TestCase):
    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_tomorrow_is_after_yesterday(self, hours, minutes):
        self.assertGreater(tomorrow(hours, minutes), yesterday(hours, minutes))

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_tomorrow_minus_yesterday_is_two_days(self, hours, minutes):
        # Both use hours/minutes consistently → difference is exactly 2 days
        delta = tomorrow(hours, minutes) - yesterday(hours, minutes)
        self.assertEqual(delta, datetime.timedelta(days=2))

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_today_respects_parameters(self, hours, minutes):
        result = today(hours=hours, minutes=minutes)
        self.assertEqual(result.hour, hours)
        self.assertEqual(result.minute, minutes)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_midnight_equals_today(self, hours, minutes):
        self.assertEqual(midnight(hours, minutes), today(hours, minutes))


# ── weekday helpers ───────────────────────────────────────────────────────


class TestWeekdayFunctionsProperties(unittest.TestCase):
    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_monday_weekday_is_zero(self, hours, minutes):
        self.assertEqual(monday(hours, minutes).weekday(), 0)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_tuesday_weekday_is_one(self, hours, minutes):
        self.assertEqual(tuesday(hours, minutes).weekday(), 1)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_wednesday_weekday_is_two(self, hours, minutes):
        self.assertEqual(wednesday(hours, minutes).weekday(), 2)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_thursday_weekday_is_three(self, hours, minutes):
        self.assertEqual(thursday(hours, minutes).weekday(), 3)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_friday_weekday_is_four(self, hours, minutes):
        self.assertEqual(friday(hours, minutes).weekday(), 4)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_saturday_weekday_is_five(self, hours, minutes):
        self.assertEqual(saturday(hours, minutes).weekday(), 5)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_sunday_weekday_is_six(self, hours, minutes):
        self.assertEqual(sunday(hours, minutes).weekday(), 6)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_all_weekday_helpers_in_future(self, hours, minutes):
        now = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        for fn in [monday, tuesday, wednesday, thursday, friday, saturday, sunday]:
            self.assertGreater(fn(hours, minutes), now)


# ── week_begin / week_end ─────────────────────────────────────────────────


class TestWeekFunctionsProperties(unittest.TestCase):
    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_week_begin_is_monday(self, hours, minutes):
        # week_begin returns the most recent Monday
        self.assertEqual(week_begin(hours=hours, minutes=minutes).weekday(), 0)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_week_end_is_one_week_after_begin(self, hours, minutes):
        self.assertEqual(
            week_end(hours=hours, minutes=minutes) - week_begin(hours=hours, minutes=minutes),
            datetime.timedelta(days=7),
        )


# ── month_begin / month_end ──────────────────────────────────────────────


class TestMonthFunctionsProperties(unittest.TestCase):
    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_month_begin_is_day_one(self, hours, minutes):
        self.assertEqual(month_begin(hours, minutes).day, 1)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_month_end_is_day_one_of_next_month(self, hours, minutes):
        result = month_end(hours=hours, minutes=minutes)
        self.assertEqual(result.day, 1)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_month_end_after_month_begin(self, hours, minutes):
        self.assertGreater(month_end(hours, minutes), month_begin(hours, minutes))


# ── year_begin / year_end ───────────────────────────────────────────────


class TestYearFunctionsProperties(unittest.TestCase):
    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_year_begin_is_jan_1(self, hours, minutes):
        result = year_begin(hours, minutes)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_year_end_is_jan_1_next_year(self, hours, minutes):
        result = year_end(hours=hours, minutes=minutes)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    @given(hours=_HOURS, minutes=_MINUTES)
    @SETTINGS
    def test_year_end_after_year_begin(self, hours, minutes):
        self.assertEqual(
            year_end(hours=hours, minutes=minutes).year,
            year_begin(hours=hours, minutes=minutes).year + 1,
        )


# ── age ─────────────────────────────────────────────────────────────────


class TestAgeProperties(unittest.TestCase):
    @given(st.dates(min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today()))
    @SETTINGS
    def test_age_is_non_negative(self, birth):
        self.assertGreaterEqual(age(birth), 0)

    @given(st.dates(min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today()))
    @SETTINGS
    def test_age_approximately_equals_years_elapsed(self, birth):
        today_d = datetime.date.today()
        years = today_d.year - birth.year
        # age either equals years or years-1 (depending on whether birthday passed)
        self.assertIn(age(birth), (years, years - 1, years + 1))

    def test_birthday_today_age_is_today_minus_birth_year(self):
        today_d = datetime.date.today()
        birth = today_d.replace(year=today_d.year - 30)
        self.assertEqual(age(birth), 30)

    def test_future_birthday_yields_minus_one_year(self):
        # Birth date strictly in the future of (month, day) within current year
        today_d = datetime.date.today()
        if today_d.month < 12:
            birth = datetime.date(today_d.year - 10, 12, 31)
            self.assertEqual(age(birth), 9)


# ── timestamp_to_ms ────────────────────────────────────────────────────


class TestTimestampToMsProperties(unittest.TestCase):
    @given(st.floats(min_value=0, max_value=2e9, allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_seconds_to_ms_is_times_thousand(self, ts):
        self.assertEqual(timestamp_to_ms(ts), int(ts * 1000))

    @given(st.integers(min_value=0, max_value=2_000_000_000))
    @SETTINGS
    def test_integer_seconds_to_ms(self, ts):
        self.assertEqual(timestamp_to_ms(ts), ts * 1000)


# ── reset_datetime ─────────────────────────────────────────────────────


class TestResetDatetimeProperties(unittest.TestCase):
    @given(st.datetimes(min_value=datetime.datetime(1970, 1, 1),
                        max_value=datetime.datetime(2099, 12, 31)))
    @SETTINGS
    def test_reset_zeroes_time(self, dt):
        result = reset_datetime(dt)
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)
        self.assertEqual(result.microsecond, 0)

    @given(st.datetimes(min_value=datetime.datetime(1970, 1, 1),
                        max_value=datetime.datetime(2099, 12, 31)))
    @SETTINGS
    def test_reset_preserves_date(self, dt):
        result = reset_datetime(dt)
        self.assertEqual(result.year, dt.year)
        self.assertEqual(result.month, dt.month)
        self.assertEqual(result.day, dt.day)
