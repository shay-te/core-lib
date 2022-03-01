import unittest
from datetime import datetime, date
from time import sleep

from omegaconf import OmegaConf

from core_lib.error_handling.status_code_exception import StatusCodeException
from examples.test_core_lib.core_lib.test_core_lib import TestCoreLib


class CoreLibTesting(TestCoreLib):

    def __init__(self):
        db_conf = {
            'create_db': True,
            'log_queries': False,
            'session': {'pool_recycle': 3600, 'pool_pre_ping': False},
            'url': {'protocol': 'sqlite'},
        }
        conf = OmegaConf.create({"db": db_conf})
        TestCoreLib.__init__(self, conf)


class TestExamples(unittest.TestCase):

    def test_example_crud(self):
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
                'gender': 1,
            }
        core_lib = CoreLibTesting()
        core_lib.user.create(user_data)
        db_data = core_lib.user.get(1)
        user_data.update({
            'id': 1,
            'birthday': datetime.combine(dattime, datetime.min.time()).timestamp(),
            'updated_at': db_data['created_at'],
            'created_at': db_data['created_at'],
            'deleted_at': None,
        })
        self.assertDictEqual(db_data, user_data)
        core_lib.user.delete(1)
        with self.assertRaises(StatusCodeException):
            core_lib.user.get(1)

    def test_example_test_data_access(self):
        core_lib = CoreLibTesting()
        self.assertEqual(core_lib.test.test_1.get_value(), 1)
        self.assertEqual(core_lib.test.test_2.get_value(), 2)

    def test_example_large_data(self):
        data_1 = {"fruit1": "apple"}
        data_2 = {"fruit2": "orange"}

        core_lib = CoreLibTesting()

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
