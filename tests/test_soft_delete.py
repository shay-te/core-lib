import unittest
from datetime import datetime
from time import sleep

from sqlalchemy import Integer, Column, VARCHAR, Index

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin
from core_lib.data_transform.result_to_dict import result_to_dict

from tests.test_data.test_utils import connect_to_mem_db


class Data(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")


class DataIndex(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'user_data_index'

    INDEX_NAME_CONTACT = 'name_contact'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False)
    contact = Column(Integer, nullable=False)

    __table_args__ = (Index(INDEX_NAME_CONTACT, name, contact, 'deleted_at_token', unique=True),)


class TestSoftDelete(unittest.TestCase):
    dattime = datetime.utcnow()
    data_name_1 = "test_name_1"
    data_name_2 = "test_name_2"
    data_name_3 = "test_name_3"

    contact_1 = 123456
    contact_2 = 456789
    contact_3 = 789123

    @classmethod
    def setUpClass(cls):
        cls.db_data_session = connect_to_mem_db()

    def test_soft_delete(self):
        with self.db_data_session.get() as session:
            objects = [Data(name=self.data_name_1), Data(name=self.data_name_2), Data(name=self.data_name_3)]
            session.bulk_save_objects(objects)
        with self.db_data_session.get() as session:
            all_data = session.query(Data).all()
            converted_data = result_to_dict(all_data)
            sleep(0.1)
            self.assertEqual(converted_data[0]['name'], self.data_name_1)
            self.assertEqual(converted_data[0]['deleted_at_token'], 0)
            self.assertEqual(converted_data[0]['deleted_at'], None)
            session.query(Data).filter(Data.id == converted_data[0]['id']).update(
                {'deleted_at': self.dattime, 'deleted_at_token': int(self.dattime.timestamp())}
            )

            self.assertEqual(converted_data[1]['name'], self.data_name_2)
            self.assertEqual(converted_data[1]['deleted_at_token'], 0)
            self.assertEqual(converted_data[1]['deleted_at'], None)
            session.query(Data).filter(Data.id == converted_data[1]['id']).update(
                {'deleted_at': self.dattime, 'deleted_at_token': int(self.dattime.timestamp())}
            )

            self.assertEqual(converted_data[2]['name'], self.data_name_3)
            self.assertEqual(converted_data[2]['deleted_at_token'], 0)
            self.assertEqual(converted_data[2]['deleted_at'], None)
            session.query(Data).filter(Data.id == converted_data[2]['id']).update(
                {'deleted_at': self.dattime, 'deleted_at_token': int(self.dattime.timestamp())}
            )

            all_deleted_data = session.query(Data).all()
            convert_deleted_data = result_to_dict(all_deleted_data)

            for data in convert_deleted_data:
                self.assertNotEqual(data['deleted_at_token'], 0)
                self.assertNotEqual(data['deleted_at'], None)
                self.assertEqual(data['created_at'], data['created_at'])
                self.assertEqual(data['deleted_at_token'], int(self.dattime.timestamp()))
                self.assertEqual(data['deleted_at'], self.dattime.timestamp())
                self.assertGreater(int(data['updated_at']), int(self.dattime.timestamp()))

            self.assertEqual(convert_deleted_data[0]['name'], self.data_name_1)
            self.assertEqual(convert_deleted_data[1]['name'], self.data_name_2)
            self.assertEqual(convert_deleted_data[2]['name'], self.data_name_3)

    def _insert_data_index(self, session):
        objects = [
            DataIndex(name=self.data_name_1, contact=self.contact_1),
            DataIndex(name=self.data_name_2, contact=self.contact_2),
            DataIndex(name=self.data_name_3, contact=self.contact_3),
        ]
        session.bulk_save_objects(objects)

    def test_soft_delete_index_bulk(self):
        with self.db_data_session.get() as session:
            self._insert_data_index(session)

            all_data = session.query(DataIndex).all()
            converted_data = result_to_dict(all_data)

            session.query(DataIndex).filter(DataIndex.id == converted_data[0]['id']).update(
                {'deleted_at': self.dattime, 'deleted_at_token': int(self.dattime.timestamp())}
            )
            session.query(DataIndex).filter(DataIndex.id == converted_data[1]['id']).update(
                {'deleted_at': self.dattime, 'deleted_at_token': int(self.dattime.timestamp())}
            )
            session.query(DataIndex).filter(DataIndex.id == converted_data[2]['id']).update(
                {'deleted_at': self.dattime, 'deleted_at_token': int(self.dattime.timestamp())}
            )
            all_deleted_data = session.query(DataIndex).all()
            deleted_data = result_to_dict(all_deleted_data)
            self.assertEqual(len(deleted_data), 3)

            self._insert_data_index(session)

            all_data = session.query(DataIndex).all()
            data = result_to_dict(all_data)
            self.assertEqual(len(data), 6)

        with self.assertLogs():
            with self.assertRaises(Exception):
                with self.db_data_session.get() as session:
                    self._insert_data_index(session)

        all_data = session.query(DataIndex).all()
        data = result_to_dict(all_data)
        self.assertEqual(len(data), 6)
        session.query(DataIndex).delete()

    def test_soft_delete_index_individual(self):
        with self.db_data_session.get() as session:
            session.add(DataIndex(name=self.data_name_1, contact=self.contact_1))

            all_data = session.query(DataIndex).all()
            converted_data = result_to_dict(all_data)
            self.assertEqual(len(converted_data), 1)
            session.query(DataIndex).filter(DataIndex.id == converted_data[0]['id']).update(
                {'deleted_at': self.dattime, 'deleted_at_token': int(self.dattime.timestamp())}
            )

            session.add(DataIndex(name=self.data_name_1, contact=self.contact_1))

            all_data = session.query(DataIndex).all()
            data = result_to_dict(all_data)
            self.assertEqual(len(data), 2)

        with self.assertRaises(Exception):
            with self.db_data_session.get() as session:
                session.add(DataIndex(name=self.data_name_1, contact=self.contact_1))
