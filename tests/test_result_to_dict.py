import unittest
import datetime

from core_lib.data_transform.result_to_dict import ResultToDict, result_to_dict


class TestResultToDict(unittest.TestCase):

    def test_lists(self):
        lst = self.get_lists()
        self.assertTrue(isinstance(lst, list))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0], 1)
        self.assertEqual(lst[1], 2)
        self.assertEqual(lst[2], 3)

    def test_tuples(self):
        tpl = self.get_tuples()
        self.assertTrue(isinstance(tpl, tuple))
        for t in tpl:
            self.assertTrue(isinstance(t, tuple))

    def test_complex_object(self):
        dat = datetime.date(2022, 1, 1)
        dattime = datetime.datetime(1999, 1, 1)
        lst = [{
            'date': dat,
            'datetime': dattime
            # Add point
        }]
        result = result_to_dict(lst)
        self.assertNotEquals(result, None)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['date'], datetime.datetime(year=dat.year, month=dat.month, day=dat.day).timestamp())
        self.assertEqual(result[0]['datetime'], dattime.timestamp())

    def test_base_db_entity(self):
        # create a new DB entity
        # db entity should have most of the types
        # date, datetime, varchar, json, enum,
        pass

    @ResultToDict()
    def get_lists(self):
        return [1, 2, 3]

    @ResultToDict()
    def get_tuples(self):
        return (("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry"))

    @ResultToDict()
    def get_from_db(self):
        # insert and get ther result from the db
