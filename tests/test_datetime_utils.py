import unittest
from datetime import datetime, timedelta, date, timezone

from dateutil.utils import today as dateutils_today
from freezegun import freeze_time

from core_lib.helpers.datetime_utils import (
    year_begin,
    year_end,
    month_begin,
    month_end,
    week_begin,
    week_end,
    day_begin,
    day_end,
    tomorrow,
    today,
    yesterday,
    midnight,
    sunday,
    monday,
    tuesday,
    wednesday,
    thursday,
    friday,
    saturday,
    hour_begin,
    hour_end,
    age,
    timestamp_to_ms,
    reset_datetime,
)

FROZEN = '2024-06-15 10:30:45'


def _next_weekday(date: datetime, weekday: int):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + timedelta(days_ahead)


class TestDBRuleValidator(unittest.TestCase):
    def test_reset_date(self):
        dattime = datetime.utcnow()
        self.assertEqual(reset_datetime(dattime), dattime.replace(hour=0, minute=0, second=0, microsecond=0))
        self.assertEqual(reset_datetime(date=dattime), dattime.replace(hour=0, minute=0, second=0, microsecond=0))

    def test_yesterday(self):
        dt_yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        cl_yesterday = yesterday()
        self.assertNotEqual(cl_yesterday, None)
        self.assertEqual(cl_yesterday.minute, 0)
        self.assertEqual(cl_yesterday.hour, 0)
        self.assertEqual(cl_yesterday.day, dt_yesterday.day)
        self.assertEqual(cl_yesterday.month, dt_yesterday.month)
        self.assertEqual(cl_yesterday.year, dt_yesterday.year)

    def test_today(self):
        dtu_today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        cl_today = today()
        self.assertNotEqual(cl_today, None)
        self.assertEqual(cl_today.minute, dtu_today.minute)
        self.assertEqual(cl_today.hour, dtu_today.hour)
        self.assertEqual(cl_today.day, dtu_today.day)
        self.assertEqual(cl_today.month, dtu_today.month)
        self.assertEqual(cl_today.year, dtu_today.year)

    def test_tomorrow(self):
        dt_tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        cl_tomorrow = tomorrow()
        self.assertNotEqual(cl_tomorrow, None)
        self.assertEqual(cl_tomorrow.minute, 0)
        self.assertEqual(cl_tomorrow.hour, 0)
        self.assertEqual(cl_tomorrow.day, dt_tomorrow.day)
        self.assertEqual(cl_tomorrow.month, dt_tomorrow.month)
        self.assertEqual(cl_tomorrow.year, dt_tomorrow.year)

    def test_year(self):
        self.assertNotEqual(year_begin(), None)
        self.assertEqual(
            year_begin(), datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        )
        self.assertNotEqual(year_end(), None)
        self.assertEqual(
            year_end(),
            datetime.utcnow().replace(
                year=datetime.utcnow().year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            ),
        )

    def test_month(self):
        self.assertNotEqual(month_begin(), None)
        self.assertEqual(month_begin(), reset_datetime(datetime.utcnow().replace(day=1)))
        self.assertNotEqual(month_end(), None)
        cl_month_end = month_end()
        self.assertEqual(cl_month_end, reset_datetime((today().replace(day=1) + timedelta(days=32)).replace(day=1)))

    def test_week(self):
        self.assertNotEqual(week_begin(), None)
        self.assertEqual(week_begin(), reset_datetime(today() - timedelta(days=datetime.now(timezone.utc).weekday())))
        self.assertNotEqual(week_end(), None)
        self.assertEqual(
            week_end(), reset_datetime((today() - timedelta(days=datetime.now(timezone.utc).weekday())) + timedelta(days=7))
        )

    def test_day(self):
        self.assertNotEqual(day_begin(), None)
        self.assertEqual(day_begin(), reset_datetime(today()))
        self.assertNotEqual(day_end(), None)
        self.assertEqual(day_end(), reset_datetime(tomorrow()))

    def test_hour(self):
        self.assertNotEqual(hour_begin(), None)
        self.assertEqual(hour_begin(), reset_datetime(datetime.utcnow()).replace(hour=datetime.utcnow().hour))
        self.assertNotEqual(hour_end(), None)
        self.assertEqual(hour_end(), reset_datetime(datetime.utcnow()).replace(hour=datetime.utcnow().hour + 1))

    def test_sunday(self):
        self.assertNotEqual(sunday(), None)
        self.assertEqual(sunday(), reset_datetime(_next_weekday(today(), 6)))

    def test_monday(self):
        self.assertNotEqual(monday(), None)
        self.assertEqual(monday(), reset_datetime(_next_weekday(today(), 0)))

    def test_tuesday(self):
        self.assertNotEqual(tuesday(), None)
        self.assertEqual(tuesday(), reset_datetime(_next_weekday(today(), 1)))

    def test_wednesday(self):
        self.assertNotEqual(wednesday(), None)
        self.assertEqual(wednesday(), reset_datetime(_next_weekday(today(), 2)))

    def test_thursday(self):
        self.assertNotEqual(thursday(), None)
        self.assertEqual(thursday(), reset_datetime(_next_weekday(today(), 3)))

    def test_friday(self):
        self.assertNotEqual(friday(), None)
        self.assertEqual(friday(), reset_datetime(_next_weekday(today(), 4)))

    def test_saturday(self):
        self.assertNotEqual(saturday(), None)
        self.assertEqual(saturday(), reset_datetime(_next_weekday(today(), 5)))

    def test_midnight(self):
        self.assertEqual(midnight(), today())
        self.assertEqual(midnight().minute, 0)
        self.assertEqual(midnight().hour, 0)

    def test_age(self):
        dat = date(2020, 5, 1)
        self.assertEqual(age(dat), int((date.today() - dat).days / 365))
        dat = date(2000, 1, 1)
        self.assertEqual(age(dat), int((date.today() - dat).days / 365))
        dat = date(1990, 1, 30)
        self.assertEqual(age(dat), int((date.today() - dat).days / 365))

    def test_timestamp_to_ms(self):
        self.assertEqual(timestamp_to_ms(datetime.utcnow().timestamp()), int(datetime.utcnow().timestamp() * 1000))
        dat = datetime(2020, 5, 1, 00, 12, 25)
        self.assertEqual(timestamp_to_ms(dat.timestamp()), int(dat.timestamp() * 1000))


class TestHourParams(unittest.TestCase):
    @freeze_time(FROZEN)
    def test_hour_begin_default_minutes(self):
        result = hour_begin()
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)
        self.assertEqual(result.microsecond, 0)

    @freeze_time(FROZEN)
    def test_hour_begin_custom_minutes(self):
        result = hour_begin(minutes=30)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.second, 0)

    @freeze_time(FROZEN)
    def test_hour_end_is_one_hour_after_begin(self):
        self.assertEqual(hour_end(), hour_begin() + timedelta(hours=1))

    @freeze_time(FROZEN)
    def test_hour_end_custom_minutes(self):
        result = hour_end(minutes=15)
        self.assertEqual(result.minute, 15)
        self.assertEqual(result, hour_begin(minutes=15) + timedelta(hours=1))


class TestDayParams(unittest.TestCase):
    @freeze_time(FROZEN)
    def test_day_begin_default(self):
        result = day_begin()
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)

    @freeze_time(FROZEN)
    def test_day_begin_custom_hours(self):
        result = day_begin(hours=9)
        self.assertEqual(result.hour, 9)
        self.assertEqual(result.minute, 0)

    @freeze_time(FROZEN)
    def test_day_begin_custom_hours_and_minutes(self):
        result = day_begin(hours=8, minutes=30)
        self.assertEqual(result.hour, 8)
        self.assertEqual(result.minute, 30)

    @freeze_time(FROZEN)
    def test_day_end_default(self):
        result = day_end()
        self.assertEqual(result, day_begin() + timedelta(days=1))

    @freeze_time(FROZEN)
    def test_day_end_custom_hours_minutes(self):
        result = day_end(hours=6, minutes=30)
        self.assertEqual(result, day_begin(hours=6, minutes=30) + timedelta(days=1))

    @freeze_time(FROZEN)
    def test_day_begin_correct_date(self):
        result = day_begin()
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 6)
        self.assertEqual(result.day, 15)


class TestTodayTomorrowYesterdayParams(unittest.TestCase):
    @freeze_time(FROZEN)
    def test_today_custom_hours(self):
        result = today(hours=14)
        self.assertEqual(result.hour, 14)

    @freeze_time(FROZEN)
    def test_today_custom_hours_minutes(self):
        result = today(hours=9, minutes=45)
        self.assertEqual(result.hour, 9)
        self.assertEqual(result.minute, 45)

    @freeze_time(FROZEN)
    def test_tomorrow_custom_hours_minutes(self):
        result = tomorrow(hours=8, minutes=30)
        self.assertEqual(result.day, 16)
        self.assertEqual(result.hour, 8)
        self.assertEqual(result.minute, 30)

    @freeze_time(FROZEN)
    def test_yesterday_custom_hours_minutes(self):
        result = yesterday(hours=22, minutes=15)
        self.assertEqual(result.day, 14)
        self.assertEqual(result.hour, 22)
        self.assertEqual(result.minute, 15)

    @freeze_time(FROZEN)
    def test_midnight_same_as_today(self):
        self.assertEqual(midnight(), today())

    @freeze_time(FROZEN)
    def test_midnight_custom_params(self):
        self.assertEqual(midnight(hours=8, minutes=30), today(hours=8, minutes=30))


class TestWeekBoundaries(unittest.TestCase):
    @freeze_time(FROZEN)
    def test_week_begin_is_monday(self):
        result = week_begin()
        self.assertEqual(result.weekday(), 0)

    @freeze_time(FROZEN)
    def test_week_begin_custom_hours(self):
        result = week_begin(hours=9)
        self.assertEqual(result.hour, 9)
        self.assertEqual(result.weekday(), 0)

    @freeze_time(FROZEN)
    def test_week_end_seven_days_after_begin(self):
        self.assertEqual(week_end(), week_begin() + timedelta(days=7))

    @freeze_time(FROZEN)
    def test_week_end_custom_hours(self):
        result = week_end(hours=6, minutes=30)
        self.assertEqual(result, week_begin(hours=6, minutes=30) + timedelta(days=7))


class TestMonthBoundaries(unittest.TestCase):
    @freeze_time(FROZEN)
    def test_month_begin_is_first(self):
        result = month_begin()
        self.assertEqual(result.day, 1)
        self.assertEqual(result.month, 6)

    @freeze_time(FROZEN)
    def test_month_begin_custom_hours(self):
        result = month_begin(hours=8, minutes=30)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.hour, 8)
        self.assertEqual(result.minute, 30)

    @freeze_time(FROZEN)
    def test_month_end_is_first_of_next_month(self):
        result = month_end()
        self.assertEqual(result.month, 7)
        self.assertEqual(result.day, 1)

    @freeze_time('2024-12-15 10:00:00')
    def test_month_end_december_wraps_to_january(self):
        result = month_end()
        self.assertEqual(result.year, 2025)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    @freeze_time('2024-02-15 10:00:00')
    def test_month_end_february(self):
        result = month_end()
        self.assertEqual(result.month, 3)
        self.assertEqual(result.day, 1)


class TestYearBoundaries(unittest.TestCase):
    @freeze_time(FROZEN)
    def test_year_begin_is_jan_1(self):
        result = year_begin()
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.year, 2024)

    @freeze_time(FROZEN)
    def test_year_begin_custom_hours(self):
        result = year_begin(hours=9, minutes=30)
        self.assertEqual(result.hour, 9)
        self.assertEqual(result.minute, 30)

    @freeze_time(FROZEN)
    def test_year_end_is_jan_1_next_year(self):
        result = year_end()
        self.assertEqual(result.year, 2025)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    @freeze_time('2024-12-31 23:59:59')
    def test_year_end_on_last_day(self):
        result = year_end()
        self.assertEqual(result.year, 2025)


class TestWeekdayFunctions(unittest.TestCase):
    @freeze_time(FROZEN)
    def test_all_weekday_functions_return_future_dates(self):
        now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        for fn in [sunday, monday, tuesday, wednesday, thursday, friday, saturday]:
            result = fn()
            self.assertGreater(result, now)

    @freeze_time(FROZEN)
    def test_weekday_functions_return_correct_weekday(self):
        self.assertEqual(monday().weekday(), 0)
        self.assertEqual(tuesday().weekday(), 1)
        self.assertEqual(wednesday().weekday(), 2)
        self.assertEqual(thursday().weekday(), 3)
        self.assertEqual(friday().weekday(), 4)
        self.assertEqual(saturday().weekday(), 5)
        self.assertEqual(sunday().weekday(), 6)

    @freeze_time(FROZEN)
    def test_weekday_custom_hours_minutes(self):
        result = monday(hours=8, minutes=30)
        self.assertEqual(result.weekday(), 0)
        self.assertEqual(result.hour, 8)
        self.assertEqual(result.minute, 30)

    @freeze_time(FROZEN)
    def test_weekday_results_are_within_7_days(self):
        now = datetime.utcnow()
        for fn in [sunday, monday, tuesday, wednesday, thursday, friday, saturday]:
            result = fn()
            delta = result - now.replace(hour=0, minute=0, second=0, microsecond=0)
            self.assertLessEqual(delta.days, 7)
            self.assertGreater(delta.days, 0)


class TestUtilityFunctions(unittest.TestCase):
    def test_timestamp_to_ms_integer(self):
        self.assertEqual(timestamp_to_ms(1.0), 1000)
        self.assertEqual(timestamp_to_ms(1.5), 1500)
        self.assertEqual(timestamp_to_ms(0), 0)

    def test_timestamp_to_ms_returns_int(self):
        result = timestamp_to_ms(1234567890.123)
        self.assertIsInstance(result, int)

    def test_reset_datetime_clears_time(self):
        dt = datetime(2024, 6, 15, 14, 30, 45, 123456)
        result = reset_datetime(dt)
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)
        self.assertEqual(result.microsecond, 0)

    def test_reset_datetime_preserves_date(self):
        dt = datetime(2024, 6, 15, 14, 30, 45)
        result = reset_datetime(dt)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 6)
        self.assertEqual(result.day, 15)

    def test_age_birthday_passed_this_year(self):
        born = date(2000, 1, 1)
        expected = date.today().year - 2000
        self.assertEqual(age(born), expected)

    def test_age_birthday_not_yet_this_year(self):
        born = date(2000, 12, 31)
        expected = date.today().year - 2000 - (1 if date.today() < born.replace(year=date.today().year) else 0)
        self.assertEqual(age(born), expected)

    def test_age_born_today_is_zero(self):
        self.assertEqual(age(date.today()), 0)

    def test_age_returns_int(self):
        self.assertIsInstance(age(date(1990, 1, 1)), int)
