import unittest
from datetime import date
from time import sleep

from hydra.core.utils import configure_log

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.generate_data import generate_email, generate_random_string
from core_lib.helpers.test import load_core_lib_config
from examples.combined_core_lib.core_lib.combined_core_lib import CombineCoreLib

from examples.test_core_lib.core_lib.data_layers.data.db.user import User

configure_log(None, True)


dattime = date.today()
user_data_crud = {
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
    @classmethod
    def setUpClass(cls):
        config = load_core_lib_config('../examples/combined_core_lib/config')
        cls.combined_core_lib = CombineCoreLib(config)

    def test_01_group_services(self):
        self.assertEqual(self.combined_core_lib.test.test.test_1.get_value(), 1)
        self.assertEqual(self.combined_core_lib.test.test.test_2.get_value(), 2)

    def test_02_memcached_data(self):
        data_1 = {"str": "shalom"}
        data_2 = {"str": "toda"}

        # Get and Set
        self.combined_core_lib.test.large_data.set_data(data_1)
        self.assertEqual(self.combined_core_lib.test.large_data.get_data(), data_1)

        # Set local, get from cache
        self.combined_core_lib.test.large_data.set_data_local(data_2)
        self.assertEqual(self.combined_core_lib.test.large_data.get_data(), data_1)
        self.assertNotEqual(self.combined_core_lib.test.large_data.get_data(), data_2)

        # Wait cache expires and get data_2
        sleep(6)
        self.assertEqual(self.combined_core_lib.test.large_data.get_data(), data_2)

        # Set Data, Invalidate, Get
        self.combined_core_lib.test.large_data.set_data(data_1)
        self.assertEqual(self.combined_core_lib.test.large_data.get_data(), data_1)
        self.combined_core_lib.test.large_data.set_data(data_2)
        self.assertEqual(self.combined_core_lib.test.large_data.get_data(), data_2)

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

        user_create = self.combined_core_lib.test.user.create(user_data)
        self.assertNotEqual(user_create, None)
        self.assertEqual(user_data["username"], user_create["username"])
        self.assertEqual(user_data["password"], user_create["password"])
        self.assertEqual(user_data["nick_name"], user_create["nick_name"])
        self.assertEqual(user_data["first_name"], user_create["first_name"])
        self.assertEqual(user_data["birthday"], date.fromtimestamp(user_create["birthday"]))
        self.assertEqual(user_data["gender"], user_create["gender"])

        # Get
        user_get = self.combined_core_lib.test.user.get(user_create["id"])
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
        user_update_status = self.combined_core_lib.test.user.update(
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

        user_get = self.combined_core_lib.test.user.get(user_create["id"])
        self.assertNotEqual(user_create, None)
        self.assertEqual(user_get["username"], update_username)
        self.assertEqual(user_get["password"], update_password)
        self.assertEqual(user_get["nick_name"], update_nick_name)
        self.assertEqual(user_get["first_name"], update_first_name)
        self.assertEqual(date.fromtimestamp(user_get["birthday"]), update_birthday)
        self.assertEqual(user_get["gender"], update_gender)

        # Rules preventing to update birthday so say the rules
        self.assertRaises(
            PermissionError, self.combined_core_lib.test.user.update, user_create["id"], {"email": generate_email()}
        )

        # Create
        user_data_invalie_email = {
            "username": generate_random_string(),
            "password": generate_random_string(),
            "nick_name": generate_random_string(),
            "first_name": generate_random_string(),
            "email": 'non valid email',
            "gender": User.Gender.MALE,
        }
        self.assertRaises(PermissionError, self.combined_core_lib.test.user.create, user_data_invalie_email)

    def test_example_crud(self):
        user = self.combined_core_lib.test.customer.create(user_data_crud)
        db_data = self.combined_core_lib.test.customer.get(user[User.id.key])
        self.assertDictEqual(db_data, user)
        sleep(0.1)
        self.combined_core_lib.test.customer.update(user[User.id.key], {'email': 'jon@doe.com'})
        db_data = self.combined_core_lib.test.customer.get(user[User.id.key])
        self.assertEqual(db_data[User.email.key], 'jon@doe.com')
        self.assertGreater(db_data[User.updated_at.key], db_data[User.created_at.key])

        self.combined_core_lib.test.customer.delete(user[User.id.key])
        with self.assertRaises(StatusCodeException):
            self.combined_core_lib.test.customer.get(user[User.id.key])
