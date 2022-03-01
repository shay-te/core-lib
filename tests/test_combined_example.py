import os
import unittest
from datetime import date, datetime
from time import sleep

import hydra
from dotenv import load_dotenv
from hydra.core.utils import configure_log
from pathlib import Path

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.generate_data import generate_email, generate_random_string
from examples.combined_core_lib.core_lib.combined_core_lib import CombineCoreLib

from examples.test_core_lib.core_lib.data_layers.data.db.user import User

configure_log(None, True)

current_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
test_output_path = os.path.normpath(os.path.join(current_path, 'test_output'))
example_path = os.path.normpath(os.path.join(current_path, '../', 'examples'))
combined_core_lib_path = os.path.join(example_path, 'combined_core_lib')
env_path = Path(os.path.join(current_path, 'test_data', 'load_env.env'))
load_dotenv(dotenv_path=env_path)

config_directory = os.path.join(combined_core_lib_path, 'config')
config_file = 'config.yaml'
hydra.initialize(config_path='../examples/combined_core_lib/config')
config = hydra.compose(config_file)

solr_core = "demo"

core_lib = CombineCoreLib(config.core_lib)

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

class TestCombinedExample(unittest.TestCase):
    def test_01_group_services(self):
        self.assertEqual(core_lib.test.test.test_1.get_value(), 1)
        self.assertEqual(core_lib.test.test.test_2.get_value(), 2)

    def test_02_memcached_data(self):
        data_1 = {"str": "shalom"}
        data_2 = {"str": "toda"}

        # Get and Set
        core_lib.test.large_data.set_data(data_1)
        self.assertEqual(core_lib.test.large_data.get_data(), data_1)

        # Set local, get from cache
        core_lib.test.large_data.set_data_local(data_2)
        self.assertEqual(core_lib.test.large_data.get_data(), data_1)
        self.assertNotEqual(core_lib.test.large_data.get_data(), data_2)

        # Wait cache expires and get data_2
        sleep(6)
        self.assertEqual(core_lib.test.large_data.get_data(), data_2)

        # Set Data, Invalidate, Get
        core_lib.test.large_data.set_data(data_1)
        self.assertEqual(core_lib.test.large_data.get_data(), data_1)
        core_lib.test.large_data.set_data(data_2)
        self.assertEqual(core_lib.test.large_data.get_data(), data_2)

    def test_03_core_lib_test_user_create_get(self):
        # Create
        user_data = {
            "username": generate_random_string(),
            "password": generate_random_string(),
            "nick_name": generate_random_string(),
            "first_name": generate_random_string(),
            "email": generate_email(),
            "birthday": date.today(),
            "gender": User.Gender.MALE.value,
        }

        user_create = core_lib.test.user.create(user_data)
        self.assertNotEqual(user_create, None)
        self.assertEqual(user_data["username"], user_create["username"])
        self.assertEqual(user_data["password"], user_create["password"])
        self.assertEqual(user_data["nick_name"], user_create["nick_name"])
        self.assertEqual(user_data["first_name"], user_create["first_name"])
        self.assertEqual(user_data["birthday"], date.fromtimestamp(user_create["birthday"]))
        self.assertEqual(user_data["gender"], user_create["gender"])

        # Get
        user_get = core_lib.test.user.get(user_create["id"])
        self.assertNotEqual(user_create, None)
        self.assertEqual(user_get["username"], user_create["username"])
        self.assertEqual(user_get["password"], user_create["password"])
        self.assertEqual(user_get["nick_name"], user_create["nick_name"])
        self.assertEqual(user_get["first_name"], user_create["first_name"])
        self.assertEqual(user_get["birthday"], user_create["birthday"])
        self.assertEqual(user_get["gender"], user_create["gender"])

        # Update
        update_username = generate_random_string()
        update_password = generate_random_string()
        update_nick_name = generate_random_string()
        update_first_name = generate_random_string()
        update_birthday = date.today()
        update_gender = User.Gender.FEMALE.value
        user_update_status = core_lib.test.user.update(
            user_create["id"],
            {
                "username": update_username,
                "password": update_password,
                "nick_name": update_nick_name,
                "first_name": update_first_name,
                "birthday": update_birthday,
                "gender": update_gender,
            },
        )
        self.assertEqual(user_update_status, 1)

        user_get = core_lib.test.user.get(user_create["id"])
        self.assertNotEqual(user_create, None)
        self.assertEqual(user_get["username"], update_username)
        self.assertEqual(user_get["password"], update_password)
        self.assertEqual(user_get["nick_name"], update_nick_name)
        self.assertEqual(user_get["first_name"], update_first_name)
        self.assertEqual(date.fromtimestamp(user_get["birthday"]), update_birthday)
        self.assertEqual(user_get["gender"], update_gender)

        # Rules preventing to update birthday so say the rules
        self.assertRaises(PermissionError, core_lib.test.user.update, user_create["id"], {"email": generate_email()})

        # Create
        user_data_invalie_email = {
            "username": generate_random_string(),
            "password": generate_random_string(),
            "nick_name": generate_random_string(),
            "first_name": generate_random_string(),
            "email": 'non valid email',
            "gender": User.Gender.MALE,
        }
        self.assertRaises(PermissionError, core_lib.test.user.create, user_data_invalie_email)

    def test_example_crud(self):

        user = core_lib.test.user_crud.create(user_data)
        db_data = core_lib.test.user_crud.get(user['id'])
        user_data.update({
            'id': user['id'],
            'birthday': datetime.combine(dattime, datetime.min.time()).timestamp(),
            'updated_at': db_data['created_at'],
            'created_at': db_data['created_at'],
            'deleted_at': None,
        })
        self.assertDictEqual(db_data, user_data)

        core_lib.test.user_crud.update(user['id'], {'email': 'jon@doe.com'})
        db_data = core_lib.test.user_crud.get(user['id'])
        self.assertEqual(db_data['email'], 'jon@doe.com')
        self.assertNotEqual(db_data['created_at'], db_data['updated_at'])

        core_lib.test.user_crud.delete(user['id'])
        with self.assertRaises(StatusCodeException):
            core_lib.test.user_crud.get(user['id'])
