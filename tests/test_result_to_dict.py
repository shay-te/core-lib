import unittest
import datetime
from dateutil.utils import today

from core_lib.data_transform.result_to_dict import ResultToDict



class TestResultToDict(unittest.TestCase):

    test_value_lists = [datetime.datetime.utcnow()]
    test_value_tuples = (("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry"))
    result_dict = {}

    def test_lists(self):
        self.assertTrue(isinstance(self.get_lists(), list))

    def test_tuples(self):
        print(self.get_tuples())
        self.assertTrue(isinstance(self.get_tuples(), tuple))


    @ResultToDict()
    def get_lists(self):
        return TestResultToDict.test_value_lists

    @ResultToDict()
    def get_tuples(self):
        return TestResultToDict.test_value_tuples


