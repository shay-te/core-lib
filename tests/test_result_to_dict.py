import enum
import json
import os.path
import unittest
import datetime

import pymongo

from sqlalchemy import Integer, Column, VARCHAR, DateTime, Enum, JSON, TEXT, Date, BLOB, Float, Boolean, Unicode
from geoalchemy2 import WKTElement

from core_lib.data_transform.result_to_dict import ResultToDict, result_to_dict
from core_lib.data_layers.data.db.sqlalchemy.base import Base

from tests.test_data.test_utils import connect_to_mem_db, connect_to_mongo


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


def convert_str_to_dict(result):
    obj = result.get('object')
    if obj and isinstance(obj, str):
        result['object'] = json.loads(obj)
    return result


def convert_return_none(result) -> dict:
    return None


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
        obj = {"fruit1": "apple", "fruit2": "orange"}
        lst_object = [
            {
                'date': dat,
                'datetime': dattime,
                'object': {
                    'object_1': {
                        'object_2': {'tuple': tpl, 'list': lst, 'point': point, 'set': set_value, 'object': obj}
                    }
                },
            }
        ]
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
        with open(os.path.join(os.path.dirname(__file__), 'test_data/koala.jpeg'), 'rb') as file:
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
            self.assertEqual(
                converted_data[0]['data_date'],
                datetime.datetime(year=data_date.year, month=data_date.month, day=data_date.day).timestamp(),
            )
            self.assertEqual(converted_data[0]['data_name'], data_name)
            self.assertEqual(converted_data[0]['data_text'], data_text)
            self.assertEqual(converted_data[0]['data_json'], data_json)
            self.assertEqual(converted_data[0]['data_blob'], data_blob)
            self.assertEqual(converted_data[0]['data_float'], data_float)
            self.assertEqual(converted_data[0]['data_bool'], data_bool)
            self.assertEqual(converted_data[0]['data_unicode'], data_unicode)

    def test_callback(self):
        json_value = {
            'userId': 1,
            'id': 1,
            'title': 'Some Title',
            'object': '{"value": "JSON in Python", "number": 123}',
        }
        data = result_to_dict(json_value, callback=convert_str_to_dict)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['userId'], 1)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], 'Some Title')
        self.assertDictEqual(data['object'], {"value": "JSON in Python", "number": 123})

        json_value_nested = {
            "userId": 1,
            "id": 1,
            "title": "Some Title",
            "object": "{\"value\": \"JSON in Python\", \"number\": 123}",
            "object_1": {"object_2": {"object_3": {"object": "{\"value\": \"JSON in Python\", \"number\": 123}"}}},
        }
        data_nested = result_to_dict(json_value_nested, callback=convert_str_to_dict)
        self.assertIsInstance(data_nested, dict)
        self.assertEqual(data_nested['userId'], 1)
        self.assertEqual(data_nested['id'], 1)
        self.assertEqual(data_nested['title'], 'Some Title')
        self.assertDictEqual(
            data_nested['object_1']['object_2']['object_3']['object'], {"value": "JSON in Python", "number": 123}
        )
        self.assertDictEqual(data_nested['object'], {"value": "JSON in Python", "number": 123})

        json_value_without_str_obj = {
            'userId': 1,
            'id': 1,
            'title': 'Some Title',
        }
        data = result_to_dict(json_value_without_str_obj, callback=convert_return_none)
        self.assertDictEqual(data, json_value_without_str_obj)

    def test_pymongo_to_dict(self):
        with connect_to_mongo().get() as client:
            collection = client.testing_db.example
            data_not_converted = collection.find()
            data_converted = result_to_dict(collection.find())
            self.assertEqual(len(data_converted), 0)
            self.assertIsInstance(data_converted, list)
            self.assertNotIsInstance(data_converted, pymongo.cursor.Cursor)
            self.assertNotEqual(data_not_converted, data_converted)

            sample_entry = {'name': 'rahul'}
            collection.insert_one(sample_entry)
            new_data = result_to_dict(collection.find())
            self.assertIsInstance(new_data[0], dict)
            self.assertEqual(new_data[0]['name'], sample_entry['name'])
            self.assertIsInstance(new_data, list)
            self.assertNotIsInstance(new_data, pymongo.cursor.Cursor)

            collection.delete_one(sample_entry)
            db_data = result_to_dict(collection.find())
            self.assertEqual(len(db_data), 0)

            new_users = [{'name': 'robin'}, {'name': 'adam'}, {'name': 'robert'}]
            collection.insert_many(new_users)
            current_db_data = result_to_dict(collection.find())
            self.assertEqual(len(current_db_data), 3)
            self.assertEqual(current_db_data[0]['name'], 'robin')
            self.assertEqual(current_db_data[1]['name'], 'adam')
            self.assertEqual(current_db_data[2]['name'], 'robert')

            collection.delete_many({})
            curr_db_data = result_to_dict(collection.find())
            self.assertEqual(len(curr_db_data), 0)

    @ResultToDict()
    def get_from_params(self, param):
        return param
