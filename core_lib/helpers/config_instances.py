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
