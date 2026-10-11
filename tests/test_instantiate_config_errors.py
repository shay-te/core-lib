"""instantiate_config's errors name the expected base class and the missing class config path."""
import unittest

from omegaconf import OmegaConf

from core_lib.cache.cache_handler import CacheHandler
from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.helpers.config_instances import instantiate_config

RAM_CACHE_CONFIG = {'_target_': 'core_lib.cache.cache_handler_ram.CacheHandlerRam'}


class TestInstantiateConfigErrors(unittest.TestCase):

    def test_wrong_base_class_names_both_classes(self):
        with self.assertRaises(ValueError) as context:
            instantiate_config(OmegaConf.create(RAM_CACHE_CONFIG), ConnectionFactory)

        cause = str(context.exception.__cause__)
        self.assertEqual(
            'object from config must be a baseclass of : `ConnectionFactory`. got `CacheHandlerRam` ', cause
        )
        self.assertNotIn('ABCMeta', cause)

    def test_right_base_class_builds_the_object(self):
        cache_handler = instantiate_config(OmegaConf.create(RAM_CACHE_CONFIG), CacheHandler)
        self.assertEqual('CacheHandlerRam', type(cache_handler).__qualname__)

    def test_missing_class_config_path_names_the_path(self):
        config = OmegaConf.create({'other': RAM_CACHE_CONFIG})
        with self.assertRaises(ValueError) as context:
            instantiate_config(config, class_config_base_path='cleanup.handler', raise_class_config_base_path_error=True)

        self.assertEqual('class config path `cleanup.handler` does not exist', str(context.exception.__cause__))

    def test_missing_class_config_path_without_raise_returns_none(self):
        config = OmegaConf.create({'other': RAM_CACHE_CONFIG})
        self.assertIsNone(instantiate_config(config, class_config_base_path='cleanup.handler'))
