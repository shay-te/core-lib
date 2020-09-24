import datetime
import unittest

from core_lib.helpers.timedelta_utils import beginning_of_month


class TestTimedeltaUtils(unittest.TestCase):

    def test_function(self):
        now = datetime.datetime.now()
        month_now = now.month
        delta_next_month = beginning_of_month()
        next_month = delta_next_month + now
        self.assertGreater(next_month.month, month_now)



