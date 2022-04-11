import unittest
from datetime import date

import hydra
from omegaconf import DictConfig

from core_lib.client.client_base import ClientBase
from core_lib.core_lib import CoreLib
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.config_instances import instantiate_config
from examples.test_core_lib.core_lib.data_layers.data.db.user import User

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


class ExampleCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        config_file = 'instantiate_sql_alchemy.yaml'
        config = hydra.compose(config_file)
        self.db_session = instantiate_config(config.config)
        self.client = instantiate_config(config.client)


class CustomerClient(ClientBase):
    def __init__(self, target_url):
        ClientBase.__init__(self, target_url)

    def get(self, customer_id: int):
        return {'customer_id': customer_id, 'username': 'Jon'}


class TestInstantiateConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        hydra.core.global_hydra.GlobalHydra.instance().clear()
        hydra.initialize(config_path='./test_data/test_config')

    def test_example_class(self):
        config_file = 'instantiate_config_example.yaml'
        config = hydra.compose(config_file)
        self.example_class = instantiate_config(config.config)
        self.assertTrue(isinstance(self.example_class.db_session, SqlAlchemyDataHandlerRegistry))

    def test_core_lib(self):
        config_file = 'instantiate_config_test_core_lib.yaml'
        config = hydra.compose(config_file)

        self.test_core_lib = instantiate_config(config.core_lib)
        user = self.test_core_lib.customer.create(user_data)
        db_data = self.test_core_lib.customer.get(user[User.id.key])
        self.assertDictEqual(db_data, user)

        self.test_core_lib.customer.update(user[User.id.key], {'email': 'jon@doe.com'})
        db_data = self.test_core_lib.customer.get(user[User.id.key])
        self.assertEqual(db_data[User.email.key], 'jon@doe.com')
        self.assertGreater(db_data[User.updated_at.key], db_data[User.created_at.key])

        self.test_core_lib.customer.delete(user[User.id.key])
        with self.assertRaises(StatusCodeException):
            self.test_core_lib.customer.get(user[User.id.key])

        self.assertEqual(self.test_core_lib.test.test_1.get_value(), 1)
        self.assertEqual(self.test_core_lib.test.test_2.get_value(), 2)
