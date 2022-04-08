---
id: instantiate_config
title: Instantiate Config
sidebar_label: Instantiate Config
---

# Instantiate Config
`instantiate_config` produces a class object instance with the configuration specified in a yaml [link](https://github.com/facebookresearch/hydra/blob/740f1446189e26d3e4a3d8c6222a50560a521820/hydra/_internal/instantiate/_instantiate2.py#L148).
It is a wrapper for the hydra's `instantiate()` for creating objects, with added capabilities of checking the 
subtype and instantiating multiple instances using the `instantiate_config_group_generator_list()` , `instantiate_config_group_generator_dict()`. 
For more info about hydra's `instantiate()` [click here](https://hydra.cc/docs/advanced/instantiate_objects/overview/)
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
Can be loaded from a YAML file using [hydra compose](https://hydra.cc/docs/1.0/experimental/compose_api/).

`instance_base_class` (*object*): An abstract class object (if any) used to validate if the `_target_` is a subclass of this type.

`class_config_base_path` (*str*): If the `_target_` key is under a nested `dict` the path needs to be specified here for the function to discover it.

`raise_class_config_base_path_error` (*bool*): If true raise an error if `_target_` was not found in `class_config_base_path`.

`params` (*dict*): Parameters to pass while instantiating the class (if any).


## Example
customer_core_lib.yaml
```yaml
core_lib:
  customer_core_lib:
    db:
      log_queries: false
      create_db: true
      session:
        pool_recycle: 3600
        pool_pre_ping: false
      url:
        protocol: postgresql
        username: ${oc.env:POSTGRES_USER}
        password: ${oc.env:POSTGRES_PASSWORD}
        host: ${oc.env:POSTGRES_HOST}
        port: ${oc.env:POSTGRES_PORT}
        file: ${oc.env:POSTGRES_DB}
```

sql_alchemy_config.yaml
```yaml
config:
  _target_: core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry.SqlAlchemyDataHandlerRegistry
  config:
    log_queries: false
    create_db: true
    session:
      pool_recycle: 3600
      pool_pre_ping: false
    url:
      protocol: sqlite
```

CustomerCoreLib.py

```python
from omegaconf import DictConfig
import hydra
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from core_lib.helpers.config_instances import instantiate_config
from core_lib.core_lib import CoreLib

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='./path/to/your/config_dir')

class CustomerCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        config = hydra.compose('sql_alchemy_config.yaml')
        # instantiate SqlAlchemyDataHandlerRegistry from sql_alchemy_config.yaml
        self.db_session = instantiate_config(config.config) 
        # initialize SqlAlchemyDataHandlerRegistry from the main config file customer_core_lib.yaml
        self.db_session = SqlAlchemyDataHandlerRegistry(self.config.core_lib.customer_core_lib.db)


config_file = 'config.yaml'
config = hydra.compose('customer_core_lib.yaml')
customer_core_lib = CustomerCoreLib(config)
isinstance(customer_core_lib.db_session, SqlAlchemyDataHandlerRegistry) #True
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

Similar to `instantiate_config_group_generator_dict`, gets a `ListConfig` instead of `DictConfig` for multiple sett