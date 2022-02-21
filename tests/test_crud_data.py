import unittest

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
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool),
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, DataSoftDelete, connect_to_mem_db(), DataCRUDSoftDeleteDataAccess.rules_validator)


class DataSoftDeleteToken(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'crud_softdel_token_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)


class DataCRUDSoftDeleteTokenDataAccess(CRUDSoftDeleteWithTokenDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool),
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, DataSoftDeleteToken, connect_to_mem_db(), DataCRUDSoftDeleteTokenDataAccess.rules_validator)


class TestCrud(unittest.TestCase):
    def test_crud(self):
        crud = DataCRUDDataAccess()

        crud.create({'name': 'test_name', 'email': 'abc@def.com', 'active': True})

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 1, 'name': 'test_name', 'email': 'abc@def.com', 'active': True})

        crud.update(1, {'active': False})

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 1, 'name': 'test_name', 'email': 'abc@def.com', 'active': False})

        crud.delete(1)

        with self.assertRaises(StatusCodeException):
            crud.get(1)

    def test_crud_multiple(self):
        dict_1 = {'name': 'Jon', 'email': 'jon@def.com', 'active': True}
        dict_2 = {'name': 'Ron', 'email': 'ron@def.com', 'active': True}
        dict_3 = {'name': 'Sam', 'email': 'sam@def.com', 'active': True}
        dict_4 = {'name': 'Jinny', 'email': 'jinny@def.com', 'active': True}
        dict_5 = {'name': 'Rosa', 'email': 'rosa@def.com', 'active': True}

        crud = DataCRUDDataAccess()

        crud.create(dict_1)
        crud.create(dict_2)
        crud.create(dict_3)
        crud.create(dict_4)
        crud.create(dict_5)

        dict_1['id'] = 1
        dict_2['id'] = 2
        dict_3['id'] = 3
        dict_4['id'] = 4
        dict_5['id'] = 5

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_1)

        data = result_to_dict(crud.get(2))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_2)

        data = result_to_dict(crud.get(3))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_3)

        data = result_to_dict(crud.get(4))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_4)

        data = result_to_dict(crud.get(5))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_5)

        crud.update(1, {'active': False})
        dict_1['active'] = False

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_1)

        crud.update(5, {'name': 'Rosita', 'email': 'rosita@def.com'})
        dict_5['name'] = 'Rosita'
        dict_5['email'] = 'rosita@def.com'

        data = result_to_dict(crud.get(5))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_5)

        crud.delete(2)
        with self.assertRaises(StatusCodeException):
            crud.get(2)

        crud.delete(3)
        with self.assertRaises(StatusCodeException):
            crud.get(3)

        crud.delete(4)
        with self.assertRaises(StatusCodeException):
            crud.get(4)

    def test_crud_soft_delete(self):
        dict_1 = {'name': 'Jon', 'email': 'jon@def.com', 'active': True}
        dict_2 = {'name': 'Ron', 'email': 'ron@def.com', 'active': True}
        dict_3 = {'name': 'Sam', 'email': 'sam@def.com', 'active': True}
        dict_4 = {'name': 'Jinny', 'email': 'jinny@def.com', 'active': True}
        dict_5 = {'name': 'Rosa', 'email': 'rosa@def.com', 'active': True}

        crud = DataCRUDSoftDeleteDataAccess()

        crud.create(dict_1)
        crud.create(dict_2)
        crud.create(dict_3)
        crud.create(dict_4)
        crud.create(dict_5)

        data = result_to_dict(crud.get(1))
        dict_1.update({'id': 1, 'deleted_at': None, 'created_at': data['created_at'], 'updated_at': data['created_at']})
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_1)

        data = result_to_dict(crud.get(2))
        dict_2.update({'id': 2, 'deleted_at': None, 'created_at': data['created_at'], 'updated_at': data['created_at']})
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_2)

        data = result_to_dict(crud.get(3))
        dict_3.update({'id': 3, 'deleted_at': None, 'created_at': data['created_at'], 'updated_at': data['created_at']})
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_3)

        data = result_to_dict(crud.get(4))
        dict_4.update({'id': 4, 'deleted_at': None, 'created_at': data['created_at'], 'updated_at': data['created_at']})
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_4)

        data = result_to_dict(crud.get(5))
        dict_5.update({'id': 5, 'deleted_at': None, 'created_at': data['created_at'], 'updated_at': data['created_at']})
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_5)

        crud.update(5, {'name': 'Rosita', 'email': 'rosita@def.com'})

        data = result_to_dict(crud.get(5))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 5)
        self.assertEqual(data['name'], 'Rosita')
        self.assertEqual(data['email'], 'rosita@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertNotEqual(data['updated_at'], data['created_at'])

        crud.delete(2)
        with self.assertRaises(StatusCodeException):
            crud.get(2)

        crud.delete(3)
        with self.assertRaises(StatusCodeException):
            crud.get(3)

        crud.delete(4)
        with self.assertRaises(StatusCodeException):
            crud.get(4)

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_1)

    def test_crud_soft_delete_token(self):
        dict_1 = {'name': 'Jon', 'email': 'jon@def.com', 'active': True}
        dict_2 = {'name': 'Ron', 'email': 'ron@def.com', 'active': True}
        dict_3 = {'name': 'Sam', 'email': 'sam@def.com', 'active': True}
        dict_4 = {'name': 'Jinny', 'email': 'jinny@def.com', 'active': True}
        dict_5 = {'name': 'Rosa', 'email': 'rosa@def.com', 'active': True}

        crud = DataCRUDSoftDeleteTokenDataAccess()

        crud.create(dict_1)
        crud.create(dict_2)
        crud.create(dict_3)
        crud.create(dict_4)
        crud.create(dict_5)

        data = result_to_dict(crud.get(1))
        dict_1.update(
            {
                'id': 1,
                'deleted_at': None,
                'created_at': data['created_at'],
                'updated_at': data['created_at'],
                'delete_token': None,
            }
        )
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_1)

        data = result_to_dict(crud.get(2))
        dict_2.update(
            {
                'id': 2,
                'deleted_at': None,
                'created_at': data['created_at'],
                'updated_at': data['created_at'],
                'delete_token': None,
            }
        )
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_2)

        data = result_to_dict(crud.get(3))
        dict_3.update(
            {
                'id': 3,
                'deleted_at': None,
                'created_at': data['created_at'],
                'updated_at': data['created_at'],
                'delete_token': None,
            }
        )
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_3)

        data = result_to_dict(crud.get(4))
        dict_4.update(
            {
                'id': 4,
                'deleted_at': None,
                'created_at': data['created_at'],
                'updated_at': data['created_at'],
                'delete_token': None,
            }
        )
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_4)

        data = result_to_dict(crud.get(5))
        dict_5.update(
            {
                'id': 5,
                'deleted_at': None,
                'created_at': data['created_at'],
                'updated_at': data['created_at'],
                'delete_token': None,
            }
        )
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_5)

        crud.update(5, {'name': 'Rosita', 'email': 'rosita@def.com'})

        data = result_to_dict(crud.get(5))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 5)
        self.assertEqual(data['name'], 'Rosita')
        self.assertEqual(data['email'], 'rosita@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['delete_token'], None)
        self.assertNotEqual(data['updated_at'], data['created_at'])

        crud.delete(2)
        with self.assertRaises(StatusCodeException):
            crud.get(2)

        crud.delete(3)
        with self.assertRaises(StatusCodeException):
            crud.get(3)

        crud.delete(4)
        with self.assertRaises(StatusCodeException):
            crud.get(4)

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, dict_1)
