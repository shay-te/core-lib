import os
import unittest
from datetime import datetime
from http import HTTPStatus
from time import sleep

from freezegun import freeze_time

from sqlalchemy import Column, Integer, VARCHAR, Boolean, UniqueConstraint
from sqlalchemy.exc import IntegrityError

from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_layers.data_access.db.crud.crud_soft_delete_data_access import CRUDSoftDeleteDataAccess
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
    description = Column(VARCHAR(length=255))


UPDATED_DESCRIPTION = 'updated description text'


def description_convertor(description: str):
    if description:
        return UPDATED_DESCRIPTION
    return None


def description_validate(description: str):
    if description:
        return True if isinstance(description, str) else False
    return True


class DataCRUDDataAccess(CRUDDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool),
        ValueRuleValidator('description', str, custom_converter=description_convertor, custom_validator=description_validate),
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
    description = Column(VARCHAR(length=255))


class DataCRUDSoftDeleteDataAccess(CRUDSoftDeleteDataAccess):
    def __init__(self):
        CRUD.__init__(self, DataSoftDelete, connect_to_mem_db())


class DataSoftDeleteToken(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'crud_softdel_token_test'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)
    description = Column(VARCHAR(length=255))


class DataCRUDSoftDeleteTokenDataAccess(CRUDSoftDeleteWithTokenDataAccess):
    def __init__(self):
        CRUD.__init__(self, DataSoftDeleteToken, connect_to_mem_db())


class Gadget(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'crud_token_gadget'

    UQ_NAME = 'uq_crud_token_gadget_name'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False)

    __table_args__ = (UniqueConstraint('name', 'deleted_at_token', name=UQ_NAME),)


class GadgetDataAccess(CRUDSoftDeleteWithTokenDataAccess):
    def __init__(self, db):
        super().__init__(Gadget, db, RuleValidator([ValueRuleValidator(Gadget.name.key, str)]))


ABSENT_ID = 2_000_000_000
CRUD_PAGE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'docs', 'pages', 'core_lib_doc', 'Data Layers', '2.crud_data_access.md',
)


class TestCrud(unittest.TestCase):
    def test_crud(self):
        crud = DataCRUDDataAccess()

        crud.create({'name': 'test_name', 'email': 'abc@def.com', 'active': True, 'description': 'Initial description'})

        data = result_to_dict(crud.get(1))
        self.assertDictEqual(data, {'id': 1, 'name': 'test_name', 'email': 'abc@def.com', 'active': True, 'description': UPDATED_DESCRIPTION})

        crud.update(1, {'active': False})

        data = result_to_dict(crud.get(1))
        self.assertDictEqual(data, {'id': 1, 'name': 'test_name', 'email': 'abc@def.com', 'active': False, 'description': UPDATED_DESCRIPTION})

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
        dict_1 = {'name': 'Jon', 'email': 'jon@def.com', 'active': True, 'description': None}
        dict_2 = {'name': 'Ron', 'email': 'ron@def.com', 'active': True, 'description': None}
        dict_3 = {'name': 'Sam', 'email': 'sam@def.com', 'active': True, 'description': None}
        dict_4 = {'name': 'Jinny', 'email': 'jinny@def.com', 'active': True, 'description': None}
        dict_5 = {'name': 'Rosa', 'email': 'rosa@def.com', 'active': True, 'description': None}

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

    def test_create_ignores_a_given_id_and_keys_the_entity_does_not_have(self):
        # No rule validator, so the dict reaches create() as given.
        crud_data_access = DataCRUDSoftDeleteDataAccess()

        created = crud_data_access.create({
            DataSoftDelete.id.key: ABSENT_ID,
            DataSoftDelete.name.key: 'widget',
            DataSoftDelete.active.key: True,
            'colour': 'blue',
        })

        self.assertNotEqual(ABSENT_ID, created.id)
        self.assertFalse(hasattr(created, 'colour'))
        self.assertEqual('widget', crud_data_access.get(created.id).name)
        with self.assertRaises(StatusCodeException):
            crud_data_access.get(ABSENT_ID)

    def test_token_soft_delete_frees_a_unique_name_for_a_new_row(self):
        gadget_data_access = GadgetDataAccess(connect_to_mem_db())
        first_gadget = gadget_data_access.create({Gadget.name.key: 'widget'})

        with self.assertRaises(IntegrityError):  # a live row already holds the name
            gadget_data_access.create({Gadget.name.key: 'widget'})
        with self.assertRaises(PermissionError):  # the rule validator given to the constructor runs on create
            gadget_data_access.create({Gadget.name.key: ['widget']})

        self.assertEqual(1, gadget_data_access.delete(first_gadget.id))
        with self.assertRaises(StatusCodeException) as missing:
            gadget_data_access.get(first_gadget.id)
        self.assertEqual(HTTPStatus.NOT_FOUND, missing.exception.status_code)

        second_gadget = gadget_data_access.create({Gadget.name.key: 'widget'})
        self.assertNotEqual(first_gadget.id, second_gadget.id)
        self.assertEqual('widget', gadget_data_access.get(second_gadget.id).name)

    def test_two_token_deletes_of_one_name_in_the_same_second_collide(self):
        # A known bug: the token is the deletion time in whole seconds, so both deleted rows would hold the same
        # (name, token). The CRUD page warns about it; a fix fails here, which is the reminder to take that off.
        gadget_data_access = GadgetDataAccess(connect_to_mem_db())
        with freeze_time('2026-01-01 10:00:00'):
            first_gadget = gadget_data_access.create({Gadget.name.key: 'widget'})
            self.assertEqual(1, gadget_data_access.delete(first_gadget.id))
            second_gadget = gadget_data_access.create({Gadget.name.key: 'widget'})
            with self.assertRaises(IntegrityError):
                gadget_data_access.delete(second_gadget.id)

        self.assertEqual('widget', gadget_data_access.get(second_gadget.id).name)    # the row stayed live
        with freeze_time('2026-01-01 10:00:01'):
            self.assertEqual(1, gadget_data_access.delete(second_gadget.id))

        with open(CRUD_PAGE, encoding='utf-8') as page:
            self.assertIn('two deletes of the same value in the same second collide', page.read())

    def test_soft_delete_of_a_deleted_row_returns_0_and_keeps_the_first_deletion(self):
        db = connect_to_mem_db()
        crud_data_access = CRUDSoftDeleteDataAccess(DataSoftDelete, db)
        widget = crud_data_access.create({DataSoftDelete.name.key: 'widget', DataSoftDelete.active.key: True})

        with freeze_time('2026-01-01 10:00:00'):
            self.assertEqual(1, crud_data_access.delete(widget.id))
        with freeze_time('2026-01-02 10:00:00'):
            self.assertEqual(0, crud_data_access.delete(widget.id))

        with db.get() as session:
            self.assertEqual(datetime(2026, 1, 1, 10, 0), session.get(DataSoftDelete, widget.id).deleted_at)

    def test_token_soft_delete_of_a_deleted_row_returns_0_and_keeps_the_first_deletion(self):
        db = connect_to_mem_db()
        gadget_data_access = GadgetDataAccess(db)
        gadget = gadget_data_access.create({Gadget.name.key: 'widget'})
        with freeze_time('2026-01-01 10:00:00'):
            self.assertEqual(1, gadget_data_access.delete(gadget.id))
        with db.get() as session:
            first_token = session.get(Gadget, gadget.id).deleted_at_token

        with freeze_time('2026-01-02 10:00:00'):
            self.assertEqual(0, gadget_data_access.delete(gadget.id))

        with db.get() as session:
            stored_gadget = session.get(Gadget, gadget.id)
        self.assertNotEqual(0, first_token)
        self.assertEqual(first_token, stored_gadget.deleted_at_token)
        self.assertEqual(datetime(2026, 1, 1, 10, 0), stored_gadget.deleted_at)
