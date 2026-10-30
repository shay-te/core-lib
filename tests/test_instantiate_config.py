import os
import unittest
from datetime import date, timedelta
from time import sleep

from omegaconf import DictConfig, OmegaConf

from core_lib.client.client_base import ClientBase
from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.config_instances import (
    instantiate_config,
    instantiate_config_group_generator_dict,
    instantiate_config_group_generator_list,
)
from core_lib.helpers.test import load_core_lib_config
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
        self.db_session = instantiate_config(self.config.core_lib.config.db)


class CustomerClient(ClientBase):
    def __init__(self, target_url):
        ClientBase.__init__(self, target_url)

    def get(self, customer_id: int):
        return {'customer_id': customer_id, 'username': 'Jon'}


class TestInstantiateConfig(unittest.TestCase):

    def test_example_core_lib(self):
        config = load_core_lib_config('./test_data/test_config', 'instantiate_config_example.yaml')
        self.example_core_lib = ExampleCoreLib(config)
        self.assertTrue(isinstance(self.example_core_lib.db_session, SqlAlchemyConnectionFactory))

    def test_core_lib(self):
        config = load_core_lib_config('./test_data/test_config', 'instantiate_config_test_core_lib.yaml')
        self.test_core_lib = instantiate_config(config.core_lib)

        self.assertIsInstance(self.test_core_lib.config.db, DictConfig)

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

        self.assertEqual(self.test_core_lib.test.test_1.get_value(), 1)
        self.assertEqual(self.test_core_lib.test.test_2.get_value(), 2)

    def test_instantiate_core_lib(self):
        config = load_core_lib_config('./test_data/test_config', 'instantiate_config_test_instantiate_core_lib.yaml')
        self.test_instantiate_core_lib = instantiate_config(config.core_lib)

        self.assertIsInstance(self.test_instantiate_core_lib.config.db, SqlAlchemyConnectionFactory)

        user = self.test_instantiate_core_lib.customer.create(user_data)
        db_data = self.test_instantiate_core_lib.customer.get(user[User.id.key])
        self.assertDictEqual(db_data, user)
        sleep(0.1)
        self.test_instantiate_core_lib.customer.update(user[User.id.key], {'email': 'jon@doe.com'})
        db_data = self.test_instantiate_core_lib.customer.get(user[User.id.key])
        self.assertEqual(db_data[User.email.key], 'jon@doe.com')
        self.assertGreater(db_data[User.updated_at.key], db_data[User.created_at.key])

        self.test_instantiate_core_lib.customer.delete(user[User.id.key])
        with self.assertRaises(StatusCodeException):
            self.test_instantiate_core_lib.customer.get(user[User.id.key])

        self.assertEqual(self.test_instantiate_core_lib.test.test_1.get_value(), 1)
        self.assertEqual(self.test_instantiate_core_lib.test.test_2.get_value(), 2)

    def test_class_config_base_path_nested(self):
        settings = OmegaConf.create({'outer': {'inner': {'_target_': 'datetime.timedelta', 'seconds': 5}}})
        self.assertEqual(timedelta(seconds=5), instantiate_config(settings, class_config_base_path='outer.inner'))

    def test_class_config_base_path_missing_gives_none(self):
        settings = OmegaConf.create({'cleanup': {'frequency': '1d', 'handler': {'_target_': 'datetime.timedelta', 'hours': 2}}})

        self.assertEqual(timedelta(hours=2), instantiate_config(settings, class_config_base_path='cleanup.handler'))
        self.assertIsNone(instantiate_config(settings, class_config_base_path='cleanup.missing'))
        self.assertIsNone(instantiate_config(settings, class_config_base_path='other.handler'))
        self.assertIsNone(instantiate_config(OmegaConf.create({})))

    def test_group_generators_build_one_object_per_entry(self):
        timeouts = OmegaConf.create({
            'short': {'note': 'health checks', 'handler': {'_target_': 'datetime.timedelta', 'minutes': 5}},
            'long': {'note': 'reports', 'handler': {'_target_': 'datetime.timedelta', 'hours': 1}},
        })
        built = [
            (name, timeout, settings.note)
            for name, timeout, settings in instantiate_config_group_generator_dict(timeouts, class_config_base_path='handler')
        ]
        self.assertEqual([('short', timedelta(minutes=5), 'health checks'), ('long', timedelta(hours=1), 'reports')], built)

        items = OmegaConf.create([
            {'_target_': 'datetime.timedelta', 'days': 1},
            {'_target_': 'datetime.timedelta', 'days': 2},
        ])
        built = [(timeout, settings.days) for timeout, settings in instantiate_config_group_generator_list(items)]
        self.assertEqual([(timedelta(days=1), 1), (timedelta(days=2), 2)], built)

        with_params = [timeout for timeout, _ in instantiate_config_group_generator_list(items, params={'hours': 3})]
        self.assertEqual([timedelta(days=1, hours=3), timedelta(days=2, hours=3)], with_params)

    def test_group_generator_list_builds_lazily_and_checks_each_entry(self):
        items = OmegaConf.create([
            {'_target_': 'datetime.timedelta', 'days': 1},
            {'_target_': 'datetime.date', 'year': 2024, 'month': 6, 'day': 14},
        ])
        generator = instantiate_config_group_generator_list(items, instance_base_class=timedelta)   # nothing built yet

        first, _ = next(generator)
        self.assertEqual(timedelta(days=1), first)
        with self.assertRaises(ValueError) as wrong_type:
            next(generator)
        self.assertEqual(
            'object from config must be a baseclass of : `timedelta`. got `date` ',
            str(wrong_type.exception.__cause__),
        )

        with self.assertRaises(AssertionError):
            next(instantiate_config_group_generator_list(OmegaConf.create([])))
