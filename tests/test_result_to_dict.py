import enum
import re
import time
import unittest
import datetime

from sqlalchemy import Integer, Column, VARCHAR, DateTime, Enum, JSON, TEXT, Date, BLOB, Float, Boolean, Unicode
from geoalchemy2 import WKTElement

from core_lib.data_transform.result_to_dict import ResultToDict, result_to_dict
from core_lib.data_layers.data.db.sqlalchemy.base import Base

from tests.test_data.test_utils import connect_to_mem_db

class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True, nullable=False)
    data_name = Column(VARCHAR(length=255), nullable=False, default="")
    data_datetime = Column(DateTime, nullable=False, default="")
    data_date = Column(Date, nullable=False, default="")
    data_text = Column(TEXT, nullable=False, default="")
    data_json = Column(JSON, nullable=False, default="")
    data_blob = Column(BLOB, nullable=False, default="")
    data_float = Column(Float, nullable=False, default="")
    data_bool = Column(Boolean, nullable=False, default="")
    data_unicode = Column(Unicode, nullable=False, default="")
    data_enum = Column(Enum(MyEnum))


class TestResultToDict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_data_session = connect_to_mem_db()

    def test_lists(self):
        lst = [1, 2, 3]
        self.assertTrue(isinstance(self.get_from_params(lst), list))
        self.assertListEqual(self.get_from_params(lst), lst)
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0], 1)
        self.assertEqual(lst[1], 2)
        self.assertEqual(lst[2], 3)

        empty_lst = []
        self.assertTrue(isinstance(self.get_from_params(empty_lst), list))
        self.assertListEqual(self.get_from_params(empty_lst), empty_lst)
        self.assertEqual(len(empty_lst), 0)

    def test_tuples(self):
        tpl = (("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry"))
        self.assertTrue(isinstance(self.get_from_params(tpl), tuple))
        self.assertEqual(len(tpl), 3)
        self.assertTupleEqual(self.get_from_params(tpl), tpl)
        self.assertTupleEqual(tpl[0], ("fruit", "apple"))
        self.assertTupleEqual(tpl[1], ("fruit", "banana"))
        self.assertTupleEqual(tpl[2], ("fruit", "cherry"))

        empty_tpl = ()
        self.assertTrue(isinstance(self.get_from_params(empty_tpl), tuple))
        self.assertTupleEqual(self.get_from_params(empty_tpl), empty_tpl)
        self.assertEqual(len(empty_tpl), 0)

    def test_complex_object(self):
        dat = datetime.date(2022, 1, 1)
        dattime = datetime.datetime(2022, 1, 1)
        tpl = ("fruit", "apple")
        lst = ["fruit", "apple"]
        point = WKTElement('POINT(5 45)')
        set_value = {"fruit", "apple"}
        obj = {"fruit": "apple", "fruit": "orange"}
        lst_object = [{
            'date': dat,
            'datetime': dattime,
            'object': {
                'object_1': {
                    'object_2': {
                        'tuple': tpl,
                        'list': lst,
                        'point': point,
                        'set': set_value,
                        'object': obj
                    }
                }
            }
        }]
        result = result_to_dict(lst_object)
        self.assertNotEqual(result, None)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(isinstance(result[0], dict))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['date'], datetime.datetime(year=dat.year, month=dat.month, day=dat.day).timestamp())
        self.assertEqual(result[0]['datetime'], dattime.timestamp())
        self.assertTrue(isinstance(result[0]['object'], dict))
        self.assertTrue(isinstance(result[0]['object']['object_1'], dict))
        self.assertTrue(isinstance(result[0]['object']['object_1']['object_2'], dict))
        self.assertEqual(len(result[0]['object']['object_1']['object_2']), 5)
        self.assertListEqual(result[0]['object']['object_1']['object_2']['list'], lst)
        self.assertTupleEqual(result[0]['object']['object_1']['object_2']['tuple'], tpl)
        self.assertDictEqual(result[0]['object']['object_1']['object_2']['object'], obj)
        self.assertSetEqual(result[0]['object']['object_1']['object_2']['set'], set_value)
        self.assertEqual(result[0]['object']['object_1']['object_2']['point'], point)

    def test_base_db_entity(self):
        data_date = datetime.date(2022, 1, 1)
        data_datetime = datetime.datetime.utcnow()
        data_name = "test_name"
        data_text = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum"
        data_json = {"key1": "value1", "key2": "value2"}
        data_float = 14.0987
        data_bool = True
        data_unicode = chr(57344)
        with open('./test_data/koala.jpeg', 'rb') as file:
            data_blob = file.read()
        with self.__class__.db_data_session.get() as session:
            data = Data()
            data.data_name = data_name
            data.data_text = data_text
            data.data_json = data_json
            data.data_blob = data_blob
            data.data_float = data_float
            data.data_bool = data_bool
            data.data_unicode = data_unicode
            data.data_datetime = data_datetime
            data.data_date = data_date
            data.data_enum = MyEnum.one
            session.add(data)

        with self.__class__.db_data_session.get() as session:
            all_data = session.query(Data).all()
            converted_data = self.get_from_params(all_data)
            self.assertNotEqual(converted_data, None)
            self.assertTrue(isinstance(converted_data, list))
            self.assertEqual(len(converted_data), 1)
            self.assertEqual(converted_data[0]['id'], 1)
            self.assertEqual(converted_data[0]['data_enum'], 1)
            self.assertEqual(converted_data[0]['data_datetime'], data_datetime.timestamp())
            self.assertEqual(converted_data[0]['data_date'], datetime.datetime(year=data_date.year, month=data_date.month, day=data_date.day).timestamp())
            self.assertEqual(converted_data[0]['data_name'], data_name)
            self.assertEqual(converted_data[0]['data_text'], data_text)
            self.assertEqual(converted_data[0]['data_json'], data_json)
            self.assertEqual(converted_data[0]['data_blob'], data_blob)
            self.assertEqual(converted_data[0]['data_float'], data_float)
            self.assertEqual(converted_data[0]['data_bool'], data_bool)
            self.assertEqual(converted_data[0]['data_unicode'], data_unicode)

    @ResultToDict()
    def get_from_params(self, param):
        return param
