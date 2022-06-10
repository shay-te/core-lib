import hydra
from omegaconf import OmegaConf

from core_lib.core_lib import CoreLib
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry


def connect_to_mem_db():
    conf = {
        'create_db': True,
        'log_queries': False,
        'session': {'pool_recycle': 3600, 'pool_pre_ping': False},
        'url': {'protocol': 'sqlite'},
    }
    return SqlAlchemyDataHandlerRegistry(OmegaConf.create(conf))


def sync_create_core_lib_config(path: str, config_file: str = 'config.yaml'):
    [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
    [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    hydra.initialize(config_path=path)
    config = hydra.compose(config_file)
    return config
