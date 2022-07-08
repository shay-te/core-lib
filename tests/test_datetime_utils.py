import unittest
from datetime import datetime, timedelta, date
from dateutil.utils import today as dateutils_today

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
        dt_yesterday = datetime.today() - timedelta(days=1)
        cl_yesterday = yesterday()
        self.assertNotEqual(cl_yesterday, None)
        self.assertEqual(cl_yesterday.minute, 0)
        self.assertEqual(cl_yesterday.hour, 0)
        self.assertEqual(cl_yesterday.day, dt_yesterday.day)
        self.assertEqual(cl_yesterday.month, dt_yesterday.month)
        self.assertEqual(cl_yesterday.year, dt_yesterday.year)

    def test_today(self):
        dtu_today = dateutils_today()
        cl_today = today()
        self.assertNotEqual(cl_today, None)
        self.assertEqual(cl_today.minute, dtu_today.minute)
        self.assertEqual(cl_today.hour, dtu_today.hour)
        self.assertEqual(cl_today.day, dtu_today.day)
        self.assertEqual(cl_today.month, dtu_today.month)
        self.assertEqual(cl_today.year, dtu_today.year)

    def test_tomorrow(self):
        dt_tomorrow = datetime.today() + timedelta(days=1)
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
        self.assertEqual(week_begin(), reset_datetime(today() - timedelta(days=datetime.today().weekday())))
        self.assertNotEqual(week_end(), None)
        self.assertEqual(
            week_end(), reset_datetime((today() - timedelta(days=datetime.today().weekday())) + timedelta(days=7))
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
