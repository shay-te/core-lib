import unittest
from datetime import date
from time import sleep

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.test import load_core_lib_config
from examples.test_core_lib.core_lib.data_layers.data.db.user import User
from examples.test_core_lib.core_lib.test_core_lib import TestCoreLib

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
    @classmethod
    def setUp(cls):
        config = load_core_lib_config('../examples/test_core_lib/config')
        cls.test_core_lib = TestCoreLib(config)

    def test_example_crud(self):
        user = self.test_core_lib.customer.create(user_data)
        db_data = self.test_core_lib.customer.get(user[User.id.key])
        self.assertDictEqual(db_data, user)
        sleep(0.1)
        self.test_core_lib.customer.update(user[User.id.key], {'email': 'jon@doe.com'})
        db_data = self.test_core_lib.customer.get(user[User.id.key])
        self.assertEqual(db_data[User.email.key], 'jon@doe.com')
        self.assertGreater(db_data[User.updated_at.key], db_data[User.created_at.key])

        self.test_core_lib.customer.delete(user[User.id.key])
        with self.assertRaises(StatusCodeException):
            self.test_core_lib.customer.get(user[User.id.key])

    def test_example_user_data_access(self):
        user = self.test_core_lib.user.create(user_data)
        db_data = self.test_core_lib.user.get(user[User.id.key])
        self.assertDictEqual(db_data, user)
        sleep(0.1)
        self.test_core_lib.user.update(user[User.id.key], {'gender': User.Gender.FEMALE.value})
        db_data = self.test_core_lib.user.get(user[User.id.key])
        self.assertEqual(db_data[User.gender.key], User.Gender.FEMALE.value)
        self.assertGreater(db_data[User.updated_at.key], db_data[User.created_at.key])

    def test_example_test_data_access(self):
        self.assertEqual(self.test_core_lib.test.test_1.get_value(), 1)
        self.assertEqual(self.test_core_lib.test.test_2.get_value(), 2)

    def test_example_large_data(self):
        data_1 = {"fruit1": "apple"}
        data_2 = {"fruit2": "orange"}

        self.test_core_lib.large_data.set_data(data_1)
        self.assertEqual(self.test_core_lib.large_data.get_data(), data_1)

        self.test_core_lib.large_data.set_data_local(data_2)
        self.assertEqual(self.test_core_lib.large_data.get_data(), data_1)
        self.assertNotEqual(self.test_core_lib.large_data.get_data(), data_2)
        sleep(6)

        self.assertEqual(self.test_core_lib.large_data.get_data(), data_2)
