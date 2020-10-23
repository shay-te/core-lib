from hydra.utils import instantiate
from omegaconf import DictConfig, ListConfig


def from_config_dict(conf: DictConfig, instance_base_class: object = None, class_config_path: str = None, class_config_path_error: bool = False):
    assert conf
    for name, settings in conf.items():
        instance, settings = _load(settings, instance_base_class, class_config_path, class_config_path_error)
        yield name, instance, settings


def from_config_list(conf: ListConfig, instance_base_class: object = None, class_config_path: str = None, class_config_path_error: bool = False):
    assert conf
    for settings in conf:
        instance, settings = _load(settings, instance_base_class, class_config_path, class_config_path_error)
        yield instance, settings


def _load(settings: dict, instance_base_class: object = None, class_config_path: str = None, class_config_path_error: bool = False):
    try:
        class_settings = _class_settings(settings, class_config_path, class_config_path_error)
        instance = None
        if class_settings:
            instance = instantiate(class_settings)
            if instance_base_class and not isinstance(instance, instance_base_class):
                raise ValueError("object from config must be a baseclass of : `{}`. got `{}` ".format(instance_base_class.__class__.__qualname__, instance.__class__.__qualname__))
        return instance, settings
    except Exception as ex:
        raise ValueError('unable to instantiate with config: `{}`'.format(settings)) from ex


def _class_settings(settings: dict, class_config_path: str, class_config_path_error: bool = False):
    class_settings = settings
    if class_config_path:
        for path in class_config_path.split('.'):
            class_settings = class_settings.get(path)
            if not class_settings:
                if class_config_path_error:
                    raise ValueError('class config path dose no exists')
                else:
                    class_settings = None
    return class_settings
