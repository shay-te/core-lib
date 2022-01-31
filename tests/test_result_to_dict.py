import enum
import unittest
import datetime

from sqlalchemy import Integer, Column, VARCHAR, DateTime, Enum, JSON, TEXT
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
    data_text = Column(TEXT, nullable=False, default="")
    data_json = Column(JSON, nullable=False, default="")
    data_enum = Column(Enum(MyEnum))


class TestResultToDict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_data_session = connect_to_mem_db()

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
            'datetime': dattime,
            'point': WKTElement('POINT(5 45)')
        }]
        result = result_to_dict(lst)
        self.assertNotEqual(result, None)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['date'], datetime.datetime(year=dat.year, month=dat.month, day=dat.day).timestamp())
        self.assertEqual(result[0]['datetime'], dattime.timestamp())

    def test_base_db_entity(self):
        with self.__class__.db_data_session.get() as session:
            data = Data()
            data.data_name = "test_name"
            data.data_text = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum "
            data.data_json = {"key1": "value1", "key2": "value2"}
            data.data_datetime = datetime.datetime.utcnow()
            data.data_enum = MyEnum.one
            session.add(data)
            session.commit()
            session.flush()
            session.close()

        with self.__class__.db_data_session.get() as session:
            all_data = session.query(Data).all()
            dt_res_to_dic = self.get_from_db(all_data)
            self.assertNotEqual(dt_res_to_dic, None)
            self.assertTrue(isinstance(dt_res_to_dic, list))
            self.assertEqual(len(dt_res_to_dic), 1)
            self.assertEqual(dt_res_to_dic[0]['id'], 1)
            self.assertEqual(dt_res_to_dic[0]['data_enum'], 1)
            self.assertEqual(dt_res_to_dic[0]['data_name'], "test_name")
            self.assertEqual(dt_res_to_dic[0]['data_text'], "Lorem Ipsum is simply dummy text of the printing and "
                                                            "typesetting industry. Lorem Ipsum ")
            self.assertEqual(dt_res_to_dic[0]['data_json'], {"key1": "value1", "key2": "value2"})

    @ResultToDict()
    def get_lists(self):
        return [1, 2, 3]

    @ResultToDict()
    def get_tuples(self):
        return (("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry"))

    @ResultToDict()
    def get_from_db(self, data_from_db):
        return data_from_db
