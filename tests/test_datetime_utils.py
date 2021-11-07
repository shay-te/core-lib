import datetime
import unittest
from datetime import timedelta

from dateutil.utils import today

from core_lib.helpers.datetime_utils import year_begin, year_end, yesterday, sunday, month_begin, month_end


class TestDBRuleValidator(unittest.TestCase):

    def test_query(self):
        dt_today = datetime.date.today()
        c_l_today = today()
        self.assertNotEqual(c_l_today, None)
        self.assertEqual(c_l_today.day, dt_today.day)
        self.assertEqual(c_l_today.month, dt_today.month)
        self.assertEqual(c_l_today.year, dt_today.year)

        dt_yesterday = datetime.date.today() - timedelta(days=1)
        c_l_yesterday = yesterday()
        self.assertNotEqual(c_l_yesterday, None)
        self.assertEqual(c_l_yesterday.day, dt_yesterday.day)
        self.assertEqual(c_l_yesterday.month, dt_yesterday.month)
        self.assertEqual(c_l_yesterday.year, dt_yesterday.year)

    def test_2(self):
        self.assertNotEqual(sunday() + timedelta(days=-7), None)
        self.assertNotEqual(sunday(), None)

    def test_3(self):
        self.assertNotEqual(month_begin(), None)
        self.assertNotEqual(month_end(), None)

    def test_4(self):
        self.assertNotEqual(year_begin(), None)
        self.assertNotEqual(year_end(), None)
