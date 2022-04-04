---
id: instantiate_config
title: Instantiate Config
sidebar_label: Instantiate Config
---

# Instantiate Config
`instantiate_config` produces a class object instance with the configuration specified in the form of `dict`.
```python
def instantiate_config(
    settings: dict,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
```
`settings` (*dict*): a dictionary with the key `_target_` that contains the class package path and the configuration for the `_target_` class.
Can be loaded from a YAML file using [hydra](https://hydra.cc/).

`instance_base_class` (*object*): An abstract class object (if any) used by the seficied class in `_target_`.

`class_config_base_path` (*str*): If the `_target_` key is under a nested `dict` the path needs to be specified here for the function to discover it.

`raise_class_config_base_path_error` (*bool*): If true raise an error if `_target_` was not found in `class_config_base_path`.

`params` (*dict*): Parameters to pass while instantiating the class (if any).


## Example
config.yaml
```yaml
config:
  _target_: path.to.ExampleClass
  conf:
    db:
      log_queries: false
      create_db: true
      session:
        pool_recycle: 3600
        pool_pre_ping: false
      url:
        protocol: sqlite
```

ExampleClass.py

```python
from omegaconf import DictConfig
import hydra
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from core_lib.helpers.config_instances import instantiate_config

class ExampleClass:
    def __init__(self, conf: DictConfig):
        self.config = conf
        self.db_session = SqlAlchemyDataHandlerRegistry(self.config.db)

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='./path/to/your/config_dir')

config_file = 'config.yaml'
config = hydra.compose(config_file)
example_class = instantiate_config(config.config)
isinstance(example_class.db_session, SqlAlchemyDataHandlerRegistry) #True
```

## Other Functions
### `instantiate_config_group_generator_dict`

```python
def instantiate_config_group_generator_dict(
    conf: DictConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
```
Similar to `instantiate_config` used for creating multiple instances for multiple classes.


### `instantiate_config_group_generator_list`

```python
def instantiate_config_group_generator_list(
    conf: ListConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
```

Similar to `instantiate_config_group_generator_dict`, gets a `ListConfig` instead of `DictConfig` for multiple settings.

