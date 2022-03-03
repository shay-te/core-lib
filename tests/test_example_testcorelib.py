import unittest
from datetime import datetime, date
from time import sleep

import hydra

from core_lib.core_lib import CoreLib
from core_lib.error_handling.status_code_exception import StatusCodeException
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


def sync_create_start_core_lib() -> TestCoreLib:
    [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
    [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
    config_file = 'config.yaml'
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    hydra.initialize(config_path='../examples/test_core_lib/config')
    config = hydra.compose(config_file)

    core_lib = TestCoreLib(config.core_lib)

    return core_lib


class TestExamples(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.core_lib = sync_create_start_core_lib()

    def test_example_crud(self):
        user = TestExamples.core_lib.customer.create(user_data)
        db_data = TestExamples.core_lib.customer.get(user[User.id.key])
        self.assertDictEqual(db_data, user)

        TestExamples.core_lib.customer.update(user[User.id.key], {'email': 'jon@doe.com'})
        db_data = TestExamples.core_lib.customer.get(user[User.id.key])
        self.assertEqual(db_data[User.email.key], 'jon@doe.com')
        self.assertGreater(db_data[User.updated_at.key], db_data[User.created_at.key])

        TestExamples.core_lib.customer.delete(user[User.id.key])
        with self.assertRaises(StatusCodeException):
            TestExamples.core_lib.customer.get(user[User.id.key])

    def test_example_user_data_access(self):
        user = TestExamples.core_lib.user.create(user_data)
        db_data = TestExamples.core_lib.user.get(user[User.id.key])
        self.assertDictEqual(db_data, user)

        TestExamples.core_lib.user.update(user[User.id.key], {'gender': User.Gender.FEMALE.value})
        db_data = TestExamples.core_lib.user.get(user[User.id.key])
        self.assertEqual(db_data[User.gender.key], User.Gender.FEMALE.value)
        self.assertGreater(db_data[User.updated_at.key], db_data[User.created_at.key])

    def test_example_test_data_access(self):
        self.assertEqual(TestExamples.core_lib.test.test_1.get_value(), 1)
        self.assertEqual(TestExamples.core_lib.test.test_2.get_value(), 2)

    def test_example_large_data(self):
        data_1 = {"fruit1": "apple"}
        data_2 = {"fruit2": "orange"}

        TestExamples.core_lib.large_data.set_data(data_1)
        self.assertEqual(TestExamples.core_lib.large_data.get_data(), data_1)

        TestExamples.core_lib.large_data.set_data_local(data_2)
        self.assertEqual(TestExamples.core_lib.large_data.get_data(), data_1)
        self.assertNotEqual(TestExamples.core_lib.large_data.get_data(), data_2)
        sleep(6)

        self.assertEqual(TestExamples.core_lib.large_data.get_data(), data_2)
