"""instantiate_config's errors name the expected base class and the missing class config path."""
import unittest

from omegaconf import OmegaConf

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.helpers.config_instances import instantiate_config

RAM_CACHE_CONFIG = {'_target_': 'core_lib.cache.cache_handler_ram.CacheHandlerRam'}


class TestInstantiateConfigErrors(unittest.TestCase):

    def test_wrong_base_class_names_both_classes(self):
        with self.assertRaises(ValueError) as context:
            instantiate_config(OmegaConf.create(RAM_CACHE_CONFIG), ConnectionFactory)

        self.assertEqual(
            'object from config must be a baseclass of : `ConnectionFactory`. got `CacheHandlerRam` ',
            str(context.exception.__cause__),
        )

    def test_missing_class_config_path_names_the_path(self):
        config = OmegaConf.create({'other': RAM_CACHE_CONFIG})
        with self.assertRaises(ValueError) as context:
            instantiate_config(config, class_config_base_path='cleanup.handler', raise_class_config_base_path_error=True)

        self.assertEqual('class config path `cleanup.handler` does not exist', str(context.exception.__cause__))
