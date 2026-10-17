---
id: registry
title: Registry
sidebar: core_lib_doc_sidebar
permalink: registry.html
folder: core_lib_doc
toc: false
---
Core-Lib needs to look up named instances at runtime — the right cache backend, the right observer, the right connection — without hard-coding them in business logic. `Registry` is the base class for all of these lookups: a typed key-value store where you register instances by name and retrieve them by key. Called with no key, `get()` returns the default entry, or the first registered one if no default was set.

> **Where it fits:** Infrastructure. `CacheRegistry`, `ObserverRegistry` and `ConnectionFactoryRegistry` all build on `DefaultRegistry`. You'll mostly use them through the class attributes `CoreLib.cache_registry`, `CoreLib.observer_registry` and `CoreLib.connection_factory_registry` when wiring backends in `CoreLib.__init__`. Because they are class attributes, there is one of each per process, shared by every `CoreLib` in it, so guard each registration (see [The CoreLib Class](core_lib_main_class.html#why-only-one-per-process)).

## Registry types

*core_lib.registry.registry.Registry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/registry.py){:target="_blank"}

- **`DefaultRegistry`** — generic key-value store with `register` / `unregister` / `get` / `registered`. [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py){:target="_blank"}
- **`ConnectionFactoryRegistry`** — restricted to `ConnectionFactory` instances; available as `CoreLib.connection_factory_registry`. Adds `get_or_reg(config)`, which builds a connection factory from config once and returns the same one on later calls. See [below](#connection-factory-registry). [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/connection/connection_factory_registry.py){:target="_blank"}
- **`CacheRegistry`** — restricted to `CacheHandler` instances; available as `CoreLib.cache_registry`. [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py){:target="_blank"}
- **`ObserverRegistry`** — restricted to `Observer` instances; available as `CoreLib.observer_registry`. [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer_registry.py){:target="_blank"}

## Default Registry

*core_lib.registry.default_registry.DefaultRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L4){:target="_blank"}

`DefaultRegistry` implements the `Registry` interface and provides the common behavior used by `CacheRegistry`, `ObserverRegistry` and `ConnectionFactoryRegistry`.

### Constructor

```python
class DefaultRegistry(Registry):

    def __init__(self, object_type: object):
        ...
```

**Arguments**

- **`object_type`** *`(object)`*: Type that every registered value must match.

#### Usage

```python
from core_lib.registry.default_registry import DefaultRegistry

class Customer(object):
    ...


class CustomerRegistry(DefaultRegistry):

    def __init__(self):
        DefaultRegistry.__init__(self, Customer)
```


### Functions

#### get()

*core_lib.registry.default_registry.DefaultRegistry.get()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L30){:target="_blank"}

Returns the registered object for the given key — the same instance that was passed to `register()`, not a copy.

```python
def get(self, key: str = None, *args, **kwargs):
    ...
```

**Arguments**

- **`key`** *`(str)`*: Key of the registry entry to return.



> If `get()` is called without a key, it returns the explicitly registered default, or the first registered value if no default was set.

> If the registry is empty, or the key does not exist, `get()` returns `None`.



#### Usage

```python
registry_factory.get('user_name')  # 'Jon Doe', registered in the register() example below
```



#### register()

*core_lib.registry.default_registry.DefaultRegistry.register()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L12){:target="_blank"}

Registers the key and value into the registry.

```python
def register(self, key: str, object, is_default: bool = False):
    ...
```

**Arguments**

- **`key`** *`(str)`*: A unique string to identify the registered object.
- **`object`**: Value to store under the key. Must be an instance of the registry's `object_type`.
- **`is_default`** *`(bool)`*: When multiple entries are registered, set `is_default=True` to mark this entry as the default. `get()` with no `key` returns the default.

**Raises**

- `ValueError` if the key is already registered. The registries on `CoreLib` are shared by the whole process, so guard the call: `if not CoreLib.cache_registry.get(KEY): CoreLib.cache_registry.register(KEY, ...)`.
- `ValueError` if the value is not an instance of `object_type`.
- `AssertionError` if the key or the value is empty or falsy (`None`, `''`).

#### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

user_name = 'Jon Doe'
registry_factory = DefaultRegistry(str)
registry_factory.register('user_name', user_name)
```



#### unregister()

*core_lib.registry.default_registry.DefaultRegistry.unregister()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L24){:target="_blank"}

Removes an entry from the registry.

```python
def unregister(self, key: str):
    ...
```
**Arguments**

- **`key`** *`(str)`*: Key of the entry to remove.


> If the default key is removed, the registry falls back to the first remaining entry.


#### Usage
```python
registry_factory.unregister('user_name')
```



#### registered()

*core_lib.registry.default_registry.DefaultRegistry.registered()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L36){:target="_blank"}

Returns the registered keys as a list.

```python
def registered(self):
```

#### Usage

```python
registry_factory.registered()
```

## Connection Factory Registry

*core_lib.connection.connection_factory_registry.ConnectionFactoryRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/connection/connection_factory_registry.py#L13){:target="_blank"}

A `DefaultRegistry` of `ConnectionFactory` objects. Core-Lib creates one for the whole process: `CoreLib.connection_factory_registry`. On top of the `DefaultRegistry` functions above, it has `get_or_reg()`.

### get_or_reg()

*core_lib.connection.connection_factory_registry.ConnectionFactoryRegistry.get_or_reg()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/connection/connection_factory_registry.py#L19){:target="_blank"}

Builds a connection factory from config the first time it is called, registers it, and returns that same factory on every later call with the same key. Use it when several Core-Libs in one process point at the same database: they share one engine and connection pool instead of each opening its own.

```python
def get_or_reg(self, config: DictConfig):
```

**Arguments**

- **`config`** *`(DictConfig)`*: Needs `_target_`, the connection factory class to build, and `_instance_key_`, the name to register it under. The remaining keys are passed to that class, as with [Instantiate Config](instantiate_config.html).

**Returns**

The factory registered under `_instance_key_`. It is built and registered first if it is not there yet.

- If the config has `_target_` but no `_instance_key_`, it logs a warning, builds a new factory on every call and registers nothing.
- If the config has neither, it raises `ValueError`.

Core-Lib's packaged `core_lib.yaml` config already sets `_instance_key_: sqlalchemy_connection` on its `core_lib.data.sqlalchemy` block.

#### Usage

```python
from omegaconf import OmegaConf
from core_lib.core_lib import CoreLib

db_config = OmegaConf.create({
    '_instance_key_': 'main_db',
    '_target_': 'core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory',
    'config': {'create_db': True, 'url': {'protocol': 'sqlite'}},
})

first = CoreLib.connection_factory_registry.get_or_reg(db_config)
second = CoreLib.connection_factory_registry.get_or_reg(db_config)
print(first is second)                                   # True
print(CoreLib.connection_factory_registry.registered())  # ['main_db']
```

In a `CoreLib` subclass this is one line, `db = CoreLib.connection_factory_registry.get_or_reg(config.core_lib.your_core_lib.data.db)`, where that YAML block holds the same `_instance_key_`, `_target_` and `config` keys.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="core_lib_main_class.html">Previous</a></button>
    <button class="pageNext-btn"><a href="result_to_dict.html">Next</a></button>
</div>
