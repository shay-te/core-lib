import unittest
from datetime import datetime, date
from time import sleep

import hydra

from core_lib.error_handling.status_code_exception import StatusCodeException
from examples.test_core_lib.core_lib.data_layers.data.db.user import User
from examples.test_core_lib.core_lib.test_core_lib import TestCoreLib

config_file = 'config.yaml'
hydra.initialize(config_path='../examples/test_core_lib/config')
config = hydra.compose(config_file)

core_lib = TestCoreLib(config.core_lib)

dattime = date.today()
user_data = {
    'email': 'jon@email.com',
    'username': 'jondoe',
    'password': 'jon@12345',
    'nick_name': 'jon',
    'first_name': 'Jon',
    'middle_name': 'P',
    'last_name': 'Doe',
    'birthday': dattime,
    'gender': User.Gender.MALE.value,
}

class TestExamples(unittest.TestCase):

    def test_example_crud(self):

        user = core_lib.user_crud.create(user_data)
        db_data = core_lib.user_crud.get(user['id'])
        user_data.update({
            'id': user['id'],
            'birthday': datetime.combine(dattime, datetime.min.time()).timestamp(),
            'updated_at': db_data['created_at'],
            'created_at': db_data['created_at'],
            'deleted_at': None,
        })
        self.assertDictEqual(db_data, user_data)

        core_lib.user_crud.update(user['id'], {'email': 'jon@doe.com'})
        db_data = core_lib.user_crud.get(user['id'])
        self.assertEqual(db_data['email'], 'jon@doe.com')
        self.assertNotEqual(db_data['created_at'], db_data['updated_at'])

        core_lib.user_crud.delete(user['id'])
        with self.assertRaises(StatusCodeException):
            core_lib.user_crud.get(user['id'])

    def test_example_user_data_access(self):

        user = core_lib.user.create(user_data)
        db_data = core_lib.user.get(user['id'])
        user_data.update({
            'id': user['id'],
            'birthday': datetime.combine(dattime, datetime.min.time()).timestamp(),
            'updated_at': db_data['created_at'],
            'created_at': db_data['created_at'],
            'deleted_at': None,
        })
        self.assertDictEqual(db_data, user_data)

        core_lib.user.update(user['id'], {'gender': User.Gender.FEMALE.value})
        db_data = core_lib.user.get(user['id'])
        self.assertEqual(db_data['gender'], User.Gender.FEMALE.value)
        self.assertNotEqual(db_data['created_at'], db_data['updated_at'])

    def test_example_test_data_access(self):
        self.assertEqual(core_lib.test.test_1.get_value(), 1)
        self.assertEqual(core_lib.test.test_2.get_value(), 2)

    def test_example_large_data(self):
        data_1 = {"fruit1": "apple"}
        data_2 = {"fruit2": "orange"}

        core_lib.large_data.set_data(data_1)
        self.assertEqual(core_lib.large_data.get_data(), data_1)

        core_lib.large_data.set_data_local(data_2)
        self.assertEqual(core_lib.large_data.get_data(), data_1)
        self.assertNotEqual(core_lib.large_data.get_data(), data_2)
        sleep(6)

        self.assertEqual(core_lib.large_data.get_data(), data_2)
        core_lib.large_data.set_data(data_1)
        self.assertEqual(core_lib.large_data.get_data(), data_1)
        core_lib.large_data.set_data(data_2)
        self.assertEqual(core_lib.large_data.get_data(), data_2)
