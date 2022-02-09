import unittest

from sqlalchemy import Column, Integer, VARCHAR

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from tests.test_data.test_utils import connect_to_mem_db
from core_lib.data_layers.data.db.sqlalchemy.base import Base


class Data(Base):
    __tablename__ = 'crud_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")


class TestCrud(unittest.TestCase, DataAccess):

    crud = CRUD()

    @classmethod
    def setUpClass(cls):
        cls.db_data_session = connect_to_mem_db()

    def test_create(self):
        self.crud.create(data={id: 1})