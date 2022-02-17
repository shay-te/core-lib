import unittest

from sqlalchemy import Column, Integer, VARCHAR, Boolean

from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import \
    CRUDSoftDeleteWithTokenDataAccess
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
    active = Column(Boolean, nullable=False, default="")


class CRUDInit(CRUDDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool)
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, Data, connect_to_mem_db(), CRUDInit.rules_validator)


class DataSoftDelete(Base, SoftDeleteMixin):
    __tablename__ = 'crud_softdel_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False, default="")


class CRUDSoftDeleteInit(CRUDSoftDeleteDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool)
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, DataSoftDelete, connect_to_mem_db(), CRUDSoftDeleteInit.rules_validator)


class DataSoftDeleteToken(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'crud_softdel_token_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False, default="")


class CRUDSoftDeleteTokenInit(CRUDSoftDeleteWithTokenDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool)
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, DataSoftDeleteToken, connect_to_mem_db(), CRUDSoftDeleteTokenInit.rules_validator)


class TestCrud(unittest.TestCase):

    def test_crud(self):
        crud = CRUDInit()

        crud.create({'name': 'test_name', 'email': 'abc@def.com', 'active': True})

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 1, 'name': 'test_name', 'email': 'abc@def.com', 'active': True})
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'test_name')
        self.assertEqual(data['email'], 'abc@def.com')
        self.assertEqual(data['active'], True)

        crud.update(1, {'active': False})

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 1, 'name': 'test_name', 'email': 'abc@def.com', 'active': False})
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'test_name')
        self.assertEqual(data['email'], 'abc@def.com')
        self.assertEqual(data['active'], False)

        crud.delete(1)

        with self.assertRaises(StatusCodeException):
            crud.get(1)

    def test_crud_multiple(self):
        crud = CRUDInit()

        crud.create({'name': 'Jon', 'email': 'jon@def.com', 'active': True})
        crud.create({'name': 'Ron', 'email': 'ron@def.com', 'active': True})
        crud.create({'name': 'Sam', 'email': 'sam@def.com', 'active': True})
        crud.create({'name': 'Jinny', 'email': 'jinny@def.com', 'active': True})
        crud.create({'name': 'Rosa', 'email': 'rosa@def.com', 'active': True})

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 1, 'name': 'Jon', 'email': 'jon@def.com', 'active': True})
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Jon')
        self.assertEqual(data['email'], 'jon@def.com')
        self.assertEqual(data['active'], True)

        data = result_to_dict(crud.get(2))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 2, 'name': 'Ron', 'email': 'ron@def.com', 'active': True})
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['name'], 'Ron')
        self.assertEqual(data['email'], 'ron@def.com')
        self.assertEqual(data['active'], True)

        data = result_to_dict(crud.get(3))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 3, 'name': 'Sam', 'email': 'sam@def.com', 'active': True})
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['name'], 'Sam')
        self.assertEqual(data['email'], 'sam@def.com')
        self.assertEqual(data['active'], True)

        data = result_to_dict(crud.get(4))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 4, 'name': 'Jinny', 'email': 'jinny@def.com', 'active': True})
        self.assertEqual(data['id'], 4)
        self.assertEqual(data['name'], 'Jinny')
        self.assertEqual(data['email'], 'jinny@def.com')
        self.assertEqual(data['active'], True)

        data = result_to_dict(crud.get(5))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 5, 'name': 'Rosa', 'email': 'rosa@def.com', 'active': True})
        self.assertEqual(data['id'], 5)
        self.assertEqual(data['name'], 'Rosa')
        self.assertEqual(data['email'], 'rosa@def.com')
        self.assertEqual(data['active'], True)

        crud.update(1, {'active': False})

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 1, 'name': 'Jon', 'email': 'jon@def.com', 'active': False})
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Jon')
        self.assertEqual(data['email'], 'jon@def.com')
        self.assertEqual(data['active'], False)

        crud.update(5, {'name': 'Rosita', 'email': 'rosita@def.com'})

        data = result_to_dict(crud.get(5))
        self.assertNotEqual(data, None)
        self.assertDictEqual(data, {'id': 5, 'name': 'Rosita', 'email': 'rosita@def.com', 'active': True})
        self.assertEqual(data['id'], 5)
        self.assertEqual(data['name'], 'Rosita')
        self.assertEqual(data['email'], 'rosita@def.com')
        self.assertEqual(data['active'], True)

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
        crud = CRUDSoftDeleteInit()

        crud.create({'name': 'Jon', 'email': 'jon@def.com', 'active': True})
        crud.create({'name': 'Ron', 'email': 'ron@def.com', 'active': True})
        crud.create({'name': 'Sam', 'email': 'sam@def.com', 'active': True})
        crud.create({'name': 'Jinny', 'email': 'jinny@def.com', 'active': True})
        crud.create({'name': 'Rosa', 'email': 'rosa@def.com', 'active': True})

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Jon')
        self.assertEqual(data['email'], 'jon@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

        data = result_to_dict(crud.get(2))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['name'], 'Ron')
        self.assertEqual(data['email'], 'ron@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

        data = result_to_dict(crud.get(3))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['name'], 'Sam')
        self.assertEqual(data['email'], 'sam@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

        data = result_to_dict(crud.get(4))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 4)
        self.assertEqual(data['name'], 'Jinny')
        self.assertEqual(data['email'], 'jinny@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

        data = result_to_dict(crud.get(5))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 5)
        self.assertEqual(data['name'], 'Rosa')
        self.assertEqual(data['email'], 'rosa@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

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
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Jon')
        self.assertEqual(data['email'], 'jon@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

    def test_crud_soft_delete_token(self):
        crud = CRUDSoftDeleteTokenInit()

        crud.create({'name': 'Jon', 'email': 'jon@def.com', 'active': True})
        crud.create({'name': 'Ron', 'email': 'ron@def.com', 'active': True})
        crud.create({'name': 'Sam', 'email': 'sam@def.com', 'active': True})
        crud.create({'name': 'Jinny', 'email': 'jinny@def.com', 'active': True})
        crud.create({'name': 'Rosa', 'email': 'rosa@def.com', 'active': True})

        data = result_to_dict(crud.get(1))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Jon')
        self.assertEqual(data['email'], 'jon@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['delete_token'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

        data = result_to_dict(crud.get(2))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['name'], 'Ron')
        self.assertEqual(data['email'], 'ron@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['delete_token'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

        data = result_to_dict(crud.get(3))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['name'], 'Sam')
        self.assertEqual(data['email'], 'sam@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['delete_token'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

        data = result_to_dict(crud.get(4))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 4)
        self.assertEqual(data['name'], 'Jinny')
        self.assertEqual(data['email'], 'jinny@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['delete_token'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

        data = result_to_dict(crud.get(5))
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 5)
        self.assertEqual(data['name'], 'Rosa')
        self.assertEqual(data['email'], 'rosa@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['delete_token'], None)
        self.assertEqual(data['updated_at'], data['created_at'])

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
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Jon')
        self.assertEqual(data['email'], 'jon@def.com')
        self.assertEqual(data['active'], True)
        self.assertEqual(data['deleted_at'], None)
        self.assertEqual(data['delete_token'], None)
        self.assertEqual(data['updated_at'], data['created_at'])
