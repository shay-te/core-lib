import datetime
import unittest
from datetime import datetime, timedelta

from dateutil.utils import today

from core_lib.helpers.datetime_utils import year_begin, year_end, month_begin, month_end, week_begin, week_end, day_begin, day_end, tomorrow, yesterday, midnight, sunday, monday, tuesday, wednesday, thursday, friday, saturday, hour_begin, hour_end


class TestDBRuleValidator(unittest.TestCase):

    def next_weekday(self, d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return d + timedelta(days_ahead)

    def test_yesterday(self):
        dt_yesterday = datetime.today() - timedelta(days=1)
        c_l_yesterday = yesterday()
        self.assertNotEqual(c_l_yesterday, None)
        self.assertEqual(c_l_yesterday.minute, 0)
        self.assertEqual(c_l_yesterday.hour, 0)
        self.assertEqual(c_l_yesterday.day, dt_yesterday.day)
        self.assertEqual(c_l_yesterday.month, dt_yesterday.month)
        self.assertEqual(c_l_yesterday.year, dt_yesterday.year)

    def test_today(self):
        dt_today = datetime.today()
        c_l_today = today()
        self.assertNotEqual(c_l_today, None)
        self.assertEqual(c_l_today.minute, 0)
        self.assertEqual(c_l_today.hour, 0)
        self.assertEqual(c_l_today.day, dt_today.day)
        self.assertEqual(c_l_today.month, dt_today.month)
        self.assertEqual(c_l_today.year, dt_today.year)

    def test_tomorrow(self):
        dt_tomorrow = datetime.today() - timedelta(days=-1)
        c_l_tomorrow = tomorrow()
        self.assertNotEqual(c_l_tomorrow, None)
        self.assertEqual(c_l_tomorrow.minute, 0)
        self.assertEqual(c_l_tomorrow.hour, 0)
        self.assertEqual(c_l_tomorrow.day, dt_tomorrow.day)
        self.assertEqual(c_l_tomorrow.month, dt_tomorrow.month)
        self.assertEqual(c_l_tomorrow.year, dt_tomorrow.year)

    def test_year(self):
        self.assertNotEqual(year_begin(), None)
        self.assertEqual(year_begin(), datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
        self.assertNotEqual(year_end(), None)
        self.assertEqual(year_end(), datetime.utcnow().replace(year=datetime.utcnow().year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0))

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
        self.assertNotEqual(day_end(), None)
        self.assertEqual(day_end(), tomorrow())


    def test_hour(self):
        self.assertNotEqual(hour_begin(), None)
        self.assertEqual(hour_begin(), datetime.utcnow().replace(minute=0, second=0, microsecond=0))
        self.assertNotEqual(hour_end(), None)
        self.assertEqual(hour_end(), datetime.utcnow().replace(hour=datetime.utcnow().hour + 1, minute=0, second=0, microsecond=0))

    def test_sunday(self):
        self.assertNotEqual(sunday(), None)
        self.assertEqual(sunday(), self.next_weekday(today(), 6))

    def test_monday(self):
        self.assertNotEqual(monday(), None)
        self.assertEqual(monday(), self.next_weekday(today(), 0))

    def test_tuesday(self):
        self.assertNotEqual(tuesday(), None)
        self.assertEqual(tuesday(), self.next_weekday(today(), 1))

    def test_wednesday(self):
        self.assertNotEqual(wednesday(), None)
        self.assertEqual(wednesday(), self.next_weekday(today(), 2))

    def test_thursday(self):
        self.assertNotEqual(thursday(), None)
        self.assertEqual(thursday(), self.next_weekday(today(), 3))

    def test_friday(self):
        self.assertNotEqual(friday(), None)
        self.assertEqual(friday(), self.next_weekday(today(), 4))


    def test_saturday(self):
        self.assertNotEqual(saturday(), None)
        self.assertEqual(saturday(), self.next_weekday(today(), 5))

    def test_midnight(self):
        self.assertNotEqual(midnight(), None)


