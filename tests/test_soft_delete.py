import unittest
from datetime import datetime

from sqlalchemy import Integer, Column, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin
from core_lib.data_transform.result_to_dict import result_to_dict

from tests.test_data.test_utils import connect_to_mem_db


class Data(Base, SoftDeleteMixin, SoftDeleteTokenMixin):

    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")


class TestSoftDelete(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_data_session = connect_to_mem_db()

    def test_soft_delete(self):
        data_name_1 = "test_name_1"
        data_name_2 = "test_name_2"
        data_name_3 = "test_name_3"
        with self.__class__.db_data_session.get() as session:
            objects = [Data(name=data_name_1), Data(name=data_name_2), Data(name=data_name_3)]
            session.bulk_save_objects(objects)
        with self.__class__.db_data_session.get() as session:
            dattime = datetime.utcnow()
            all_data = session.query(Data).all()
            converted_data = result_to_dict(all_data)

            self.assertEqual(converted_data[0]['name'], data_name_1)
            self.assertEqual(converted_data[0]['delete_token'], None)
            self.assertEqual(converted_data[0]['deleted_at'], None)
            session.query(Data).filter(Data.id == 1).update(
                {'deleted_at': dattime, 'delete_token': int(dattime.timestamp())}
            )

            self.assertEqual(converted_data[1]['name'], data_name_2)
            self.assertEqual(converted_data[1]['delete_token'], None)
            self.assertEqual(converted_data[1]['deleted_at'], None)
            session.query(Data).filter(Data.id == 2).update(
                {'deleted_at': dattime, 'delete_token': int(dattime.timestamp())}
            )

            self.assertEqual(converted_data[2]['name'], data_name_3)
            self.assertEqual(converted_data[2]['delete_token'], None)
            self.assertEqual(converted_data[2]['deleted_at'], None)
            session.query(Data).filter(Data.id == 3).update(
                {'deleted_at': dattime, 'delete_token': int(dattime.timestamp())}
            )

            all_deleted_data = session.query(Data).all()
            convert_deleted_data = result_to_dict(all_deleted_data)

            self.assertNotEqual(convert_deleted_data[0]['delete_token'], None)
            self.assertNotEqual(convert_deleted_data[0]['deleted_at'], None)
            self.assertEqual(convert_deleted_data[0]['name'], data_name_1)
            self.assertEqual(convert_deleted_data[0]['created_at'], converted_data[0]['created_at'])
            self.assertEqual(convert_deleted_data[0]['delete_token'], int(dattime.timestamp()))
            self.assertEqual(convert_deleted_data[0]['deleted_at'], dattime.timestamp())
            self.assertEqual(int(convert_deleted_data[0]['updated_at']), int(dattime.timestamp()))

            self.assertNotEqual(convert_deleted_data[1]['delete_token'], None)
            self.assertNotEqual(convert_deleted_data[1]['deleted_at'], None)
            self.assertEqual(convert_deleted_data[1]['name'], data_name_2)
            self.assertEqual(convert_deleted_data[1]['created_at'], converted_data[1]['created_at'])
            self.assertEqual(convert_deleted_data[1]['delete_token'], int(dattime.timestamp()))
            self.assertEqual(convert_deleted_data[1]['deleted_at'], dattime.timestamp())
            self.assertEqual(int(convert_deleted_data[1]['updated_at']), int(dattime.timestamp()))

            self.assertNotEqual(convert_deleted_data[2]['delete_token'], None)
            self.assertNotEqual(convert_deleted_data[2]['deleted_at'], None)
            self.assertEqual(convert_deleted_data[2]['name'], data_name_3)
            self.assertEqual(convert_deleted_data[2]['created_at'], converted_data[2]['created_at'])
            self.assertEqual(convert_deleted_data[2]['delete_token'], int(dattime.timestamp()))
            self.assertEqual(convert_deleted_data[2]['deleted_at'], dattime.timestamp())
            self.assertEqual(int(convert_deleted_data[2]['updated_at']), int(dattime.timestamp()))
