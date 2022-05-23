import unittest
from time import sleep

from sqlalchemy import Column, Integer, VARCHAR, Boolean

from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import (
    CRUDSoftDeleteWithTokenDataAccess,
)
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.error_handling.status_code_exception import StatusCodeException
from tests.test_data.test_utils import connect_to_mem_db
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.data_layers.data.db.sqlalchemy.base import Base


class Data(Base):
    __tablename__ = 'crud_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)


class DataCRUDDataAccess(CRUDDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool),
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, Data, connect_to_mem_db(), DataCRUDDataAccess.rules_validator)


class DataSoftDelete(Base, SoftDeleteMixin):
    __tablename__ = 'crud_softdel_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)


class DataCRUDSoftDeleteDataAccess(CRUDSoftDeleteDataAccess):
    def __init__(self):
        CRUD.__init__(self, DataSoftDelete, connect_to_mem_db())


class DataSoftDeleteToken(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'crud_softdel_token_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)


class DataCRUDSoftDeleteTokenDataAccess(CRUDSoftDeleteWithTokenDataAccess):
    def __init__(self):
        CRUD.__init__(self, DataSoftDeleteToken, connect_to_mem_db())


class TestCrud(unittest.TestCase):
    def test_crud(self):
        crud = DataCRUDDataAccess()

        crud.create({'name': 'test_name', 'email': 'abc@def.com', 'active': True})

        data = result_to_dict(crud.get(1))
        self.assertDictEqual(data, {'id': 1, 'name': 'test_name', 'email': 'abc@def.com', 'active': True})

        crud.update(1, {'active': False})

        data = result_to_dict(crud.get(1))
        self.assertDictEqual(data, {'id': 1, 'name': 'test_name', 'email': 'abc@def.com', 'active': False})

        crud.delete(1)
        with self.assertRaises(StatusCodeException):
            crud.get(1)

    def test_crud_multiple(self):
        self._test_data_access(DataCRUDDataAccess(), False, False)

    def test_crud_soft_delete(self):
        self._test_data_access(DataCRUDSoftDeleteDataAccess(), True, False)

    def test_crud_soft_delete_token(self):
        self._test_data_access(DataCRUDSoftDeleteTokenDataAccess(), True, True)

    def _compare_data(self, src_data, data_2, is_soft_delete: bool, is_token_delete: bool):
        self.assertNotEqual(src_data, None)
        self.assertNotEqual(data_2, None)
        self.assertEqual(src_data['name'], data_2['name'])
        self.assertEqual(src_data['email'], data_2['email'])
        self.assertEqual(src_data['active'], data_2['active'])
        len_append = 1  # + id
        if is_soft_delete and is_token_delete:
            len_append += 4
            self.assertEqual(int(data_2['created_at']), int(data_2['updated_at']))
            self.assertEqual(data_2['deleted_at'], None)
            self.assertEqual(data_2['deleted_at_token'], 0)
        elif is_soft_delete:
            self.assertEqual(int(data_2['created_at']), int(data_2['updated_at']))
            self.assertEqual(data_2['deleted_at'], None)
            len_append += 3
        elif is_token_delete:
            self.assertEqual(data_2['deleted_at_token'], None)
            len_append += 1
        self.assertEqual(len(src_data) + len_append, len(data_2))

    def _test_data_access(self, crud_data_access: CRUD, is_soft_delete: bool, is_token_delete: bool):
        dict_1 = {'name': 'Jon', 'email': 'jon@def.com', 'active': True}
        dict_2 = {'name': 'Ron', 'email': 'ron@def.com', 'active': True}
        dict_3 = {'name': 'Sam', 'email': 'sam@def.com', 'active': True}
        dict_4 = {'name': 'Jinny', 'email': 'jinny@def.com', 'active': True}
        dict_5 = {'name': 'Rosa', 'email': 'rosa@def.com', 'active': True}

        self.assertEqual(result_to_dict(crud_data_access.create(dict_1))['id'], 1)
        self.assertEqual(result_to_dict(crud_data_access.create(dict_2))['id'], 2)
        self.assertEqual(result_to_dict(crud_data_access.create(dict_3))['id'], 3)
        self.assertEqual(result_to_dict(crud_data_access.create(dict_4))['id'], 4)
        self.assertEqual(result_to_dict(crud_data_access.create(dict_5))['id'], 5)

        self._compare_data(dict_1, result_to_dict(crud_data_access.get(1)), is_soft_delete, is_token_delete)
        self._compare_data(dict_2, result_to_dict(crud_data_access.get(2)), is_soft_delete, is_token_delete)
        self._compare_data(dict_3, result_to_dict(crud_data_access.get(3)), is_soft_delete, is_token_delete)
        self._compare_data(dict_4, result_to_dict(crud_data_access.get(4)), is_soft_delete, is_token_delete)
        self._compare_data(dict_5, result_to_dict(crud_data_access.get(5)), is_soft_delete, is_token_delete)

        crud_data_access.update(1, {'active': False})
        self.assertEqual(result_to_dict(crud_data_access.get(1))['active'], False)
        sleep(0.1)
        crud_data_access.update(5, {'name': 'Rosita', 'email': 'rosita@def.com'})
        data_5 = result_to_dict(crud_data_access.get(5))
        self.assertEqual(data_5['name'], 'Rosita')
        self.assertEqual(data_5['email'], 'rosita@def.com')
        if is_soft_delete:
            self.assertGreater(data_5['updated_at'], data_5['created_at'])

        crud_data_access.delete(2)
        with self.assertRaises(StatusCodeException):
            crud_data_access.get(2)

        crud_data_access.delete(3)
        with self.assertRaises(StatusCodeException):
            crud_data_access.get(3)

        crud_data_access.delete(4)
        with self.assertRaises(StatusCodeException):
            crud_data_access.get(4)
