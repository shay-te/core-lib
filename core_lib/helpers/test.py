import hydra

from core_lib.core_lib import CoreLib


def load_core_lib_config(path: str, config_file: str = 'config.yaml', caller_stack_depth: int = 2):
    [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
    [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    hydra.initialize(config_path=path, caller_stack_depth=caller_stack_depth)
    config = hydra.compose(config_file)
    return config
