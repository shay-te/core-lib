import unittest
from datetime import timedelta

from dateutil.utils import today

from core_lib.helpers.datetime_utils import yesterday, saturday, sunday, month_beginning, month_end, year_beginning, \
    year_next


class TestDBRuleValidator(unittest.TestCase):

    # def test_query(self):
    #     print(yesterday())
    #     print(today())

    # def test_2(self):
    #     print(sunday() + timedelta(days=-7))
    #     print(sunday())

    # def test_3(self):
    #     print(month_beginning())
    #     print(month_end())

    def test_4(self):
        print(year_beginning())
        print(year_next())
