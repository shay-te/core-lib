---
id: instantiate_config
title: Instantiate Config
sidebar: core_lib_doc_sidebar
permalink: instantiate_config.html
folder: core_lib_doc
toc: false
---

`instantiate_config` builds an object from a config block that names its class in a `_target_` key, using Hydra's [`instantiate()`](https://hydra.cc/docs/advanced/instantiate_objects/overview/){:target="_blank"}. The class and its constructor arguments live in YAML, so a test or another deployment can swap the class by changing config, not code.

> **Optional utility.** You can use Core-Lib without calling it yourself. Inside Core-Lib, `CoreLib.connection_factory_registry.get_or_reg(...)` calls it, and `load_jobs(...)` uses its sibling `instantiate_config_group_generator_dict`. `CoreLib.__init__` itself instantiates nothing.
>
> **Where it fits:** Wiring. You call it yourself, usually in your CoreLib subclass's `__init__`, to build connection factories, clients or a nested CoreLib from YAML.

**Why not call `hydra.utils.instantiate` directly?** `instantiate_config` adds:

1. `instance_base_class`, which raises if the YAML builds an object of the wrong type.
2. `params`, runtime values merged over the YAML.
3. `class_config_base_path`, to find `_target_` under a sub-key such as `handler` or `cleanup.handler`.
4. A single `ValueError` that includes the config that failed.
5. `None` for an empty config, where Hydra would return an empty dict.
6. Group generators that yield `(name, instance, settings)` for each entry of a config group.

If you need none of these, `hydra.utils.instantiate` is fine.

## instantiate_config()

*core_lib.helpers.config_instances.instantiate_config()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/config_instances.py#L65){:target="_blank"}

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

- **`settings`** *`(dict or DictConfig)`*: The config block. It holds `_target_`, the import path of the class (or function) to call, and the constructor arguments as sibling keys. Usually loaded from a YAML file with [Hydra's compose API](https://hydra.cc/docs/advanced/compose_api/){:target="_blank"}.

- **`instance_base_class`** *`(class)`*: Optional. The created object must be an instance of this class; otherwise a `ValueError` is raised. The check runs after the object is built.

- **`class_config_base_path`** *`(str)`*: Optional. A dotted path to the sub-key that holds `_target_`, such as `'handler'` or `'cleanup.handler'`. Each part is looked up in turn. If a part is missing or empty, the function returns `None`.

- **`raise_class_config_base_path_error`** *`(bool)`*: Default `False`. When `True`, a missing `class_config_base_path` raises `ValueError` instead of returning `None`.

- **`params`** *`(dict)`*: Optional. Extra constructor arguments merged over the config's top-level keys; a key in `params` wins over the same key in the YAML.

**Returns**

The created object, or `None` when the config (at `class_config_base_path`, if given) is empty or missing.

**Raises**

`ValueError` (`unable to instantiate ..., with config: ...`) for any failure: a `_target_` that cannot be imported, a constructor that raises, an object of the wrong type, or a missing path with `raise_class_config_base_path_error=True`. The original error is attached as `__cause__`.

**Example**

```python
from datetime import timedelta

from omegaconf import OmegaConf

from core_lib.helpers.config_instances import instantiate_config

conf = OmegaConf.create({'_target_': 'datetime.timedelta', 'days': 1})

print(instantiate_config(conf))                                 # 1 day, 0:00:00
print(instantiate_config(conf, params={'days': 9}))             # 9 days, 0:00:00
print(instantiate_config(conf, instance_base_class=timedelta))  # 1 day, 0:00:00
print(instantiate_config(OmegaConf.create({})))                 # None
```

**Finding `_target_` under a sub-key**

```python
from omegaconf import OmegaConf

from core_lib.helpers.config_instances import instantiate_config

conf = OmegaConf.create({
    'cleanup': {
        'frequency': '1d',
        'handler': {'_target_': 'datetime.timedelta', 'hours': 2},
    },
})

print(instantiate_config(conf, class_config_base_path='cleanup.handler'))  # 2:00:00
print(instantiate_config(conf, class_config_base_path='cleanup.missing'))  # None

try:
    instantiate_config(conf, class_config_base_path='cleanup.missing', raise_class_config_base_path_error=True)
except ValueError:
    print('cleanup.missing not found')
```

## Examples with a CoreLib

### Building a connection factory in your CoreLib

#### `config/customer_core_lib.yaml`

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

#### `customer_core_lib.py`

```python
import hydra
from omegaconf import DictConfig

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config


class CustomerCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        self.db_factory = instantiate_config(self.config.core_lib.customer_core_lib.db)


# config_path is relative to this file
hydra.initialize(config_path='./config', version_base=None)
config = hydra.compose('customer_core_lib.yaml')
customer_core_lib = CustomerCoreLib(config)
print(isinstance(customer_core_lib.db_factory, SqlAlchemyConnectionFactory))  # True
```

This block has no `_instance_key_`, so `instantiate_config` can build it. A block that has one, such as Core-Lib's packaged `core_lib.data.sqlalchemy` defaults, must go through `CoreLib.connection_factory_registry.get_or_reg(...)` instead: `instantiate_config` would pass `_instance_key_` to the factory as a constructor argument, and the factory rejects it. `get_or_reg` removes the key, calls `instantiate_config`, and shares one factory between all the code that asks for that key (see [Registry](registry.html#connection-factory-registry)).

### A CoreLib as the target

The whole CoreLib can be the `_target_`. Hydra builds nested `_target_` blocks first (recursive instantiation, Hydra's default), so `conf.db` reaches the constructor already built.

#### `config/customer_core_lib.yaml`

```yaml
customer_core_lib:
  _target_: my_app.customer_core_lib.CustomerCoreLib   # the import path of your class
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

#### `my_app/customer_core_lib.py`

```python
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib


class CustomerCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        self.db_factory = self.config.db  # already built by Hydra
```

#### `main.py`

```python
import hydra

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.helpers.config_instances import instantiate_config

hydra.initialize(config_path='./config', version_base=None)
config = hydra.compose('customer_core_lib.yaml')
customer_core_lib = instantiate_config(config.customer_core_lib)
print(type(customer_core_lib).__name__)                                       # CustomerCoreLib
print(isinstance(customer_core_lib.db_factory, SqlAlchemyConnectionFactory))  # True
```

## Group generators

These build one object per entry of a config group. They are **generators**: nothing is built until you iterate. Both take the same optional arguments as `instantiate_config`, applied to every entry, and iterating an empty group raises `AssertionError`. `load_jobs()` uses the dict version, with `class_config_base_path='handler'`, to build each job in the config you pass it (see [Jobs](job.html)).

### instantiate_config_group_generator_dict()

*core_lib.helpers.config_instances.instantiate_config_group_generator_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/config_instances.py#L7){:target="_blank"}

For a `DictConfig` whose values are config blocks.

```python
def instantiate_config_group_generator_dict(
    conf: DictConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
```

**Yields**

`(name, instance, settings)` for each key in `conf`. `settings` is the whole entry, not only the part under `class_config_base_path`, so you can read sibling keys such as `note` below (or `frequency` for a job).

### instantiate_config_group_generator_list()

*core_lib.helpers.config_instances.instantiate_config_group_generator_list()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/config_instances.py#L22){:target="_blank"}

For a `ListConfig` whose items are config blocks.

```python
def instantiate_config_group_generator_list(
    conf: ListConfig,
    instance_base_class: object = None,
    class_config_base_path: str = None,
    raise_class_config_base_path_error: bool = False,
    params: dict = {},
):
```

**Yields**

`(instance, settings)` for each item in `conf`.

### Example

```python
from omegaconf import OmegaConf

from core_lib.helpers.config_instances import (
    instantiate_config_group_generator_dict,
    instantiate_config_group_generator_list,
)

timeouts = OmegaConf.create({
    'short': {'note': 'health checks', 'handler': {'_target_': 'datetime.timedelta', 'minutes': 5}},
    'long': {'note': 'reports', 'handler': {'_target_': 'datetime.timedelta', 'hours': 1}},
})
for name, timeout, settings in instantiate_config_group_generator_dict(timeouts, class_config_base_path='handler'):
    print(name, timeout, settings.note)
# short 0:05:00 health checks
# long 1:00:00 reports

items = OmegaConf.create([
    {'_target_': 'datetime.timedelta', 'days': 1},
    {'_target_': 'datetime.timedelta', 'days': 2},
])
for timeout, settings in instantiate_config_group_generator_list(items):
    print(timeout)
# 1 day, 0:00:00
# 2 days, 0:00:00
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="generate_data.html">Previous</a></button>
    <button class="pageNext-btn"><a href="logger.html">Next</a></button>
</div>