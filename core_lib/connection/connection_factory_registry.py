import copy
import logging
from abc import ABC

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.helpers.config_instances import instantiate_config
from core_lib.helpers.constants import InstantiateConfigConstants

from core_lib.registry.default_registry import DefaultRegistry
from omegaconf import DictConfig, OmegaConf


class ConnectionFactoryRegistry(DefaultRegistry, ABC):

    def __init__(self):
        DefaultRegistry.__init__(self, ConnectionFactory)
        self.logger = logging.getLogger(__name__)

    def get_or_reg(self, config: DictConfig):
        instance_key = config.get(InstantiateConfigConstants.INSTANCE_KEY.value)
        target = config.get(InstantiateConfigConstants.TARGET.value)

        if not instance_key and target:
            self.logger.warning('"instance_key" not found returning an instance without registering to registry')
            return instantiate_config(config)

        if not instance_key and not target:
            raise ValueError(f'{InstantiateConfigConstants.INSTANCE_KEY.value} and {InstantiateConfigConstants.TARGET.value} not found in the config')

        if not self.get(instance_key):
            # Create a deep copy (dict) to remove any references
            config_dict = OmegaConf.to_container(config, resolve=False)
            config_copy = copy.deepcopy(config_dict)
            config_copy.pop(InstantiateConfigConstants.INSTANCE_KEY.value, None)
            self.register(instance_key, instantiate_config(config_copy))

        return self.get(instance_key)
