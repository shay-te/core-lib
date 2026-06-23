from typing import Optional

from hydra.utils import instantiate
from omegaconf import DictConfig, ListConfig

from core_lib.helpers.constants import InstantiateConfigConstants


def instantiate_config_group_generator_dict(
    conf: DictConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: Optional[dict] = None,
):
    # `params=None` resolved internally — avoids the shared-mutable-default
    # Python footgun where every caller sees the same dict instance.
    """
    Generate (name, instance, settings) tuples by instantiating each entry in a DictConfig.
    
    Iterates over each key-value pair in the DictConfig, instantiates the configuration
    for each entry, and yields the key name, the instantiated object, and the original
    settings. The instance may be None if the configuration at the target path is empty
    or missing.
    
    Parameters:
        instance_base_class (object, optional): Type to validate each instantiated
            object against. If provided, each instance must be an instance of this class.
        class_config_base_path (str, optional): Dotted path to the class configuration
            within each entry's settings.
        raise_class_config_base_path_error (bool): If True, raises ValueError when the
            class_config_base_path cannot be resolved; otherwise returns None as instance.
        params (dict, optional): Parameters to merge into each configuration during
            instantiation.
    
    Yields:
        tuple: (name, instance, settings) where name is the key from the DictConfig,
            instance is the instantiated object or None, and settings is the original
            configuration.
    
    Raises:
        AssertionError: If conf is empty.
    """
    if params is None:
        params = {}
    if not conf:
        raise AssertionError('config_instances: `conf` cannot be empty')
    for name, settings in conf.items():
        instance, settings = _instantiate_config(
            settings, instance_base_class, class_config_base_path, raise_class_config_base_path_error, params
        )
        yield name, instance, settings


def instantiate_config_group_generator_list(
    conf: ListConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: Optional[dict] = None,
):
    """
    Yield instantiated objects and settings from each entry in a list configuration.
    
    Parameters:
    	conf (ListConfig): The list configuration to iterate over.
    	instance_base_class (type, optional): Expected base class for instantiated objects. If specified, each instance is validated against this class.
    	class_config_base_path (str, optional): Dotted path to the class instantiation config within each entry.
    	raise_class_config_base_path_error (bool): If True, raises ValueError when the class config path cannot be resolved; if False, yields None as the instance.
    	params (dict, optional): Shared parameters merged into each entry's instantiation config.
    
    Yields:
    	tuple: (instance, settings) pairs where instance is the instantiated object or None, and settings is the original config entry.
    
    Raises:
    	AssertionError: If conf is empty.
    """
    if params is None:
        params = {}
    if not conf:
        raise AssertionError('config_instances: `conf` cannot be empty')
    for settings in conf:
        instance, settings = _instantiate_config(
            settings, instance_base_class, class_config_base_path, raise_class_config_base_path_error, params
        )
        yield instance, settings


def _instantiate_config(
    settings: dict,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: Optional[dict] = None,
):
    """
    Instantiate a Hydra-configured object from settings with optional type validation.
    
    Parameters:
        settings (dict): Configuration dictionary containing the object definition.
        instance_base_class (object, optional): Expected base class for type validation of the instantiated object.
        class_config_base_path (str, optional): Dotted path to a nested config object within settings.
        raise_class_config_base_path_error (bool, optional): If True, raise an error when the class config path cannot be resolved.
        params (dict, optional): Additional parameters to merge into the configuration.
    
    Returns:
        tuple: (instance, settings) where instance is the instantiated object or None if configuration is empty, and settings is the original settings dictionary.
    
    Raises:
        ValueError: If instantiation fails, the instantiated object does not match instance_base_class, or the class config path is not found when raise_class_config_base_path_error is True.
    """
    if params is None:
        params = {}
    try:
        class_settings = (
            _get_config_under_path(settings, class_config_base_path, raise_class_config_base_path_error) or {}
        )
        class_settings = {**class_settings, **params}
        recursive = class_settings.get(InstantiateConfigConstants.RECURSIVE.value, True)
        if class_settings:
            instance = instantiate(class_settings, _recursive_=recursive)
            if instance_base_class and not isinstance(instance, instance_base_class):
                raise ValueError(
                    f'object from config must be a baseclass of : '
                    f'`{instance_base_class.__class__.__qualname__}`. got '
                    f'`{instance.__class__.__qualname__}` '
                )
            return instance, settings
        return None, settings
    except Exception as ex:
        raise ValueError(f'unable to instantiate {class_settings}, with config: `{settings}`') from ex


def instantiate_config(
    settings: dict,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: Optional[dict] = None,
):
    """
    Instantiate a Hydra-configured object from settings.
    
    Parameters:
        params (dict, optional): Additional parameters to merge into the class configuration, taking precedence over the settings.
    
    Returns:
        The instantiated object, or None if the class configuration is empty or missing.
    """
    if params is None:
        params = {}
    return _instantiate_config(
        settings, instance_base_class, class_config_base_path, raise_class_config_base_path_error, params
    )[0]


def _get_config_under_path(data: dict, path: Optional[str], raise_class_config_base_path_error: bool = False):
    # Previous implementation had three bugs:
    #   1. used `data.get(path)` instead of `data_at_path.get(path_item)` —
    #      so it looked up the full dotted string at the top level instead
    #      of descending one segment at a time;
    #   2. didn't update the cursor — every iteration read from the original
    #      `data` argument, so nested paths could never resolve;
    #   3. used `if not data_at_path:` which treated falsy values (0, '',
    #      [], False) as "not found".
    """
    Resolve and return the nested config object located at a dotted path within data.
    
    If the path cannot be resolved, returns None unless raise_class_config_base_path_error is True,
    in which case raises ValueError.
    
    Parameters:
        path: Dotted path string (e.g., 'a.b.c') to navigate. If None or empty, returns the root data.
        raise_class_config_base_path_error: If True, raise ValueError when the path cannot be resolved.
    
    Returns:
        The config object at the specified path, or None if the path does not exist.
    
    Raises:
        ValueError: If the path cannot be resolved and raise_class_config_base_path_error is True.
    """
    data_at_path = data
    path_list = path.split('.') if path else []
    for path_item in path_list:
        if isinstance(data_at_path, dict) and path_item in data_at_path:
            data_at_path = data_at_path[path_item]
        else:
            if raise_class_config_base_path_error:
                raise ValueError('class config path dose no exists')
            return None
    return data_at_path
