from hydra.utils import instantiate
from omegaconf import DictConfig, ListConfig


def instantiate_config_group_generator_dict(
    conf: DictConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
    assert conf
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
    params: dict = {},
):
    assert conf
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
    params: dict = {},
):
    try:
        class_settings = (
            _get_config_under_path(settings, class_config_base_path, raise_class_config_base_path_error) or {}
        )
        class_settings = {**class_settings, **params}

        if class_settings:
            instance = instantiate(class_settings)
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
    params: dict = {},
):
    return _instantiate_config(
        settings, instance_base_class, class_config_base_path, raise_class_config_base_path_error, params
    )[0]


def _get_config_under_path(data: dict, path: str, raise_class_config_base_path_error: bool = False):
    data_at_path = data
    path_list = path.split('.') if path else []
    for path_item in path_list:
        data_at_path = data.get(path) if path_item in data else None
        if not data_at_path:
            if raise_class_config_base_path_error:
                raise ValueError('class config path dose no exists')
            else:
                data_at_path = None
                break
    return data_at_path
