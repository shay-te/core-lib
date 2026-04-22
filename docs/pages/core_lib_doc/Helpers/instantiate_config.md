---
id: instantiate_config
title: Instantiate Config
sidebar: core_lib_doc_sidebar
permalink: instantiate_config.html
folder: core_lib_doc
toc: false
---

### instantiate_config()

*core_lib.helpers.config_instances.instantiate_config()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/config_instances.py#L62){:target="_blank"}

`instantiate_config` produces a class object instance with the configuration specified in a yaml [link](https://github.com/facebookresearch/hydra/blob/740f1446189e26d3e4a3d8c6222a50560a521820/hydra/_internal/instantiate/_instantiate2.py#L148){:target="_blank"}.
It is a wrapper for the hydra's `instantiate()` for creating objects, with added capabilities of checking the 
subtype and instantiating multiple instances using the `instantiate_config_group_generator_list()` , `instantiate_config_group_generator_dict()`. 
For more info about hydra's `instantiate()` [click here](https://hydra.cc/docs/advanced/instantiate_objects/overview/){:target="_blank"}

```python
def instantiate_config(
    settings: dict,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
```
**Arguments**

- **`settings`** *`(dict)`*: A dictionary with the key `_target_` that contains the class package path and the configuration for the `_target_` class.
Can be loaded from a YAML file using [hydra compose](https://hydra.cc/docs/1.0/experimental/compose_api/){:target="_blank"}.

- **`instance_base_class`** *`(object)`*: An abstract class object (if any) used to validate if the `_target_` is a subclass of this type.

- **`class_config_base_path`** *`(str)`*: If the `_target_` key is under a nested `dict` the path needs to be specified here for the function to discover it.

- **`raise_class_config_base_path_error`** *`(bool)`*: If true raise an error if `_target_` was not found in `class_config_base_path`.

- **`params`** *`(dict)`*: Additional parameters, these parameters will be merged with the yaml parameters..


### Examples

### Core-Lib Yaml with target
customer_core_lib.yaml
```yaml
core_lib:
  customer_core_lib:
    db:
      _target_: core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory
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
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.helpers.config_instances import instantiate_config
from core_lib.core_lib import CoreLib

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='./path/to/your/config_dir')


class CustomerCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        self.db_session = instantiate_config(self.config.core_lib.customer_core_lib.db)


config_file = 'config.yaml'
config = hydra.compose('customer_core_lib.yaml')
customer_core_lib = CustomerCoreLib(config)
isinstance(customer_core_lib.db_session, SqlAlchemyConnectionFactory)  # True
```

### Core-Lib as a target
customer_core_lib.yaml
```yaml
config:
  _target_: your.core_lib_path.CustomerCoreLib
  conf:
    db:
      _target_: core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory
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
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.helpers.config_instances import instantiate_config
from core_lib.core_lib import CoreLib

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='./path/to/your/config_dir')


class CustomerCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        self.db_session = self.config.db


config_file = 'config.yaml'
config = hydra.compose('customer_core_lib.yaml')
customer_core_lib = instantiate_config(config.config)
isinstance(customer_core_lib.db_session, SqlAlchemyConnectionFactory)  # True
```


## Other Functions

### instantiate_config_group_generator_dict()

*core_lib.helpers.config_instances.instantiate_config_group_generator_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/config_instances.py#L5){:target="_blank"}

Similar to `instantiate_config` used for creating multiple instances for multiple classes.

```python
def instantiate_config_group_generator_dict(
    conf: DictConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
```

### instantiate_config_group_generator_list()

*core_lib.helpers.config_instances.instantiate_config_group_generator_list()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/config_instances.py#L20){:target="_blank"}

Similar to `instantiate_config_group_generator_dict`, gets a `ListConfig` instead of `DictConfig` for multiple set

```python
def instantiate_config_group_generator_list(
    conf: ListConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/generate_data.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/logger.html">Next >></a></button>
</div>