import datetime
import unittest
from datetime import datetime, timedelta

from dateutil.utils import today

from core_lib.helpers.datetime_utils import year_begin, year_end, month_begin, month_end, week_begin, week_end, \
    day_begin, day_end, tomorrow, yesterday, midnight, sunday, monday, tuesday, wednesday, thursday, friday, saturday, \
    hour_begin, hour_end


def _next_weekday(date: datetime, weekday: int):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + timedelta(days_ahead)


class TestDBRuleValidator(unittest.TestCase):

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
        dt_today = datetime.today()
        cl_today = today()
        self.assertNotEqual(cl_today, None)
        self.assertEqual(cl_today.minute, 0)
        self.assertEqual(cl_today.hour, 0)
        self.assertEqual(cl_today.day, dt_today.day)
        self.assertEqual(cl_today.month, dt_today.month)
        self.assertEqual(cl_today.year, dt_today.year)

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
        self.assertEqual(year_begin(),
                         datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
        self.assertNotEqual(year_end(), None)
        self.assertEqual(year_end(),
                         datetime.utcnow().replace(year=datetime.utcnow().year + 1, month=1, day=1, hour=0, minute=0,
                                                   second=0, microsecond=0))

    def test_month(self):
        self.assertNotEqual(month_begin(), None)
        self.assertEqual(month_begin(), datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0))
        self.assertNotEqual(month_end(), None)
        self.assertEqual(month_end(), (today().replace(day=1) + timedelta(days=32)).replace(day=1))

    def test_week(self):
        self.assertNotEqual(week_begin(), None)
        self.assertEqual(week_begin(), today() - timedelta(days=datetime.today().weekday()))
        self.assertNotEqual(week_end(), None)
        self.assertEqual(week_end(), (today() - timedelta(days=datetime.today().weekday())) + timedelta(days=7))

    def test_day(self):
        self.assertNotEqual(day_begin(), None)
        self.assertEqual(day_begin(), today())
        self.assertEqual(day_begin().minute, 0)
        self.assertEqual(day_begin().hour, 0)
        self.assertNotEqual(day_end(), None)
        self.assertEqual(day_end(), tomorrow())
        self.assertEqual(day_end().minute, 0)
        self.assertEqual(day_end().hour, 0)

    def test_hour(self):
        self.assertNotEqual(hour_begin(), None)
        self.assertEqual(hour_begin(), datetime.utcnow().replace(minute=0, second=0, microsecond=0))
        self.assertNotEqual(hour_end(), None)
        self.assertEqual(hour_end(),
                         datetime.utcnow().replace(hour=datetime.utcnow().hour + 1, minute=0, second=0, microsecond=0))

    def test_sunday(self):
        self.assertNotEqual(sunday(), None)
        self.assertEqual(sunday(), _next_weekday(today(), 6))
        self.assertEqual(sunday().second, 0)
        self.assertEqual(sunday().minute, 0)
        self.assertEqual(sunday().hour, 0)

    def test_monday(self):
        self.assertNotEqual(monday(), None)
        self.assertEqual(monday(), _next_weekday(today(), 0))
        self.assertEqual(monday().second, 0)
        self.assertEqual(monday().minute, 0)
        self.assertEqual(monday().hour, 0)

    def test_tuesday(self):
        self.assertNotEqual(tuesday(), None)
        self.assertEqual(tuesday(), _next_weekday(today(), 1))
        self.assertEqual(tuesday().second, 0)
        self.assertEqual(tuesday().minute, 0)
        self.assertEqual(tuesday().hour, 0)

    def test_wednesday(self):
        self.assertNotEqual(wednesday(), None)
        self.assertEqual(wednesday(), _next_weekday(today(), 2))
        self.assertEqual(wednesday().second, 0)
        self.assertEqual(wednesday().minute, 0)
        self.assertEqual(wednesday().hour, 0)

    def test_thursday(self):
        self.assertNotEqual(thursday(), None)
        self.assertEqual(thursday(), _next_weekday(today(), 3))
        self.assertEqual(thursday().second, 0)
        self.assertEqual(thursday().minute, 0)
        self.assertEqual(thursday().hour, 0)

    def test_friday(self):
        self.assertNotEqual(friday(), None)
        self.assertEqual(friday(), _next_weekday(today(), 4))
        self.assertEqual(friday().second, 0)
        self.assertEqual(friday().minute, 0)
        self.assertEqual(friday().hour, 0)

    def test_saturday(self):
        self.assertNotEqual(saturday(), None)
        self.assertEqual(saturday(), _next_weekday(today(), 5))
        self.assertEqual(saturday().second, 0)
        self.assertEqual(saturday().minute, 0)
        self.assertEqual(saturday().hour, 0)

    def test_midnight(self):
        self.assertNotEqual(midnight(), None)
