import unittest

from sqlalchemy import Column, Integer, VARCHAR

from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from tests.test_data.test_utils import connect_to_mem_db
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.data_layers.data.db.sqlalchemy.base import Base


class Data(Base):
    __tablename__ = 'crud_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")


class CRUDInit(CRUDDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str)
    ]

    rules_validator = RuleValidator(allowed_update_types, mandatory_keys=['name'])

    def __init__(self):
        CRUD.__init__(self, Data, connect_to_mem_db(), CRUDInit.rules_validator)


class TestCrud(unittest.TestCase):

    def test_create(self):
        crud = CRUDInit()
        crud.create({'name': 'test_name'})
        print(crud.get(1).name)
