from hydra.core.config_store import ConfigStore
from hydra.utils import instantiate
from omegaconf import DictConfig, ListConfig


def from_config_dict(conf: DictConfig, instance_base_class: object = None, class_config_path: str = None, raise_class_config_path_error: bool = False, params: dict = None):
    assert conf
    for name, settings in conf.items():
        instance, settings = _load(settings, instance_base_class, class_config_path, raise_class_config_path_error, params)
        yield name, instance, settings


def from_config_list(conf: ListConfig, instance_base_class: object = None, class_config_path: str = None, raise_class_config_path_error: bool = False, params: dict = None):
    assert conf
    for settings in conf:
        instance, settings = _load(settings, instance_base_class, class_config_path, raise_class_config_path_error, params)
        yield instance, settings


def _load(settings: dict, instance_base_class: object = None, class_config_path: str = None, raise_class_config_path_error: bool = False, params: dict = None):
    try:
        class_settings = _class_settings(settings, class_config_path, raise_class_config_path_error)
        instance = None
        if class_settings:
            class_settings_params = {}
            for p_key, p_value in (params or {}).items():
                if p_key is not '_target_' and p_key in class_settings:
                    class_settings_params[p_key] = p_value
            instance = instantiate(class_settings, **class_settings_params)
            if instance_base_class and not isinstance(instance, instance_base_class):
                raise ValueError(f"object from config must be a baseclass of : `{instance_base_class.__class__.__qualname__}`. got `{instance.__class__.__qualname__}` ")
        return instance, settings
    except Exception as ex:
        raise ValueError('unable to instantiate with config: `{}`'.format(settings)) from ex


def _class_settings(settings: dict, class_config_path: str, raise_class_config_path_error: bool = False):
    class_settings = settings
    if class_config_path:
        for path in class_config_path.split('.'):
            class_settings = class_settings.get(path) if path in class_settings else None
            if not class_settings:
                if raise_class_config_path_error:
                    raise ValueError('class config path dose no exists')
                else:
                    class_settings = None
    return class_settings


