import copy
import logging
import threading
from abc import ABC

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.helpers.config_instances import instantiate_config
from core_lib.helpers.constants import InstantiateConfigConstants

from core_lib.registry.default_registry import DefaultRegistry
from omegaconf import DictConfig, OmegaConf


class ConnectionFactoryRegistry(DefaultRegistry, ABC):

    def __init__(self):
        """
        Initialize the ConnectionFactory registry with thread-safe concurrent access.
        
        Sets up the parent registry for ConnectionFactory type, a module logger, and a lock that serializes get_or_reg() calls to prevent concurrent threads from both instantiating and registering the same instance key.
        """
        DefaultRegistry.__init__(self, ConnectionFactory)
        self.logger = logging.getLogger(__name__)
        # Serializes the check-then-register sequence so two concurrent
        # callers can't both observe an empty slot, both instantiate, and
        # both call register() (the second one would raise ValueError on
        # the duplicate key).
        self._get_or_reg_lock = threading.Lock()

    def get_or_reg(self, config: DictConfig):
        """
        Retrieve an existing or create a new ConnectionFactory instance.
        
        Parameters:
            config (DictConfig): Configuration with 'target' (the class to instantiate) and
                'instance_key' (identifier for registry caching). If only 'target' is provided,
                returns an unregistered instance.
        
        Returns:
            ConnectionFactory: The retrieved or newly created instance.
        
        Raises:
            ValueError: If both instance_key and target are missing from the config.
        """
        instance_key = config.get(InstantiateConfigConstants.INSTANCE_KEY.value)
        target = config.get(InstantiateConfigConstants.TARGET.value)

        if not instance_key and target:
            self.logger.warning('"instance_key" not found returning an instance without registering to registry')
            return instantiate_config(config)

        if not instance_key and not target:
            raise ValueError(f'{InstantiateConfigConstants.INSTANCE_KEY.value} and {InstantiateConfigConstants.TARGET.value} not found in the config')

        # Hold the lock across check + instantiate + register so the
        # registry can be safely shared between threads.
        with self._get_or_reg_lock:
            existing = self.get(instance_key)
            if existing is not None:
                return existing
            # Create a deep copy (dict) to remove any references
            config_dict = OmegaConf.to_container(config, resolve=False)
            config_copy = copy.deepcopy(config_dict)
            config_copy.pop(InstantiateConfigConstants.INSTANCE_KEY.value, None)
            instance = instantiate_config(config_copy)
            self.register(instance_key, instance)
            return instance
