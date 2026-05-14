---
id: registry
title: Registry
sidebar: core_lib_doc_sidebar
permalink: registry.html
folder: core_lib_doc
toc: false
---
Core-Lib needs to look up named instances at runtime — the right cache backend, the right observer, the right connection — without hard-coding them in business logic. `Registry` is the base class for all of these lookups: a typed key-value store where you register instances by name and retrieve them by key (or get the default when only one is registered).

> **Where it fits:** Infrastructure. `CacheRegistry`, `ObserverRegistry`, and the connection registries all inherit from `Registry`. You'll mostly use it indirectly — through `CoreLib.cache_registry` and `CoreLib.observer_registry` — when wiring backends in `CoreLib.__init__`.

## Registry types

*core_lib.registry.Registry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/registry.py){:target="_blank"}

- **`DefaultRegistry`** — generic key-value store with `register` / `unregister` / `get` / `registered`. [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py){:target="_blank"}
- **`ConnectionFactoryRegistry`** — base class for connection factory registries. [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/connection/connection_factory_registry.py){:target="_blank"}
- **`CacheRegistry`** — restricted to `CacheHandler` instances. [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py){:target="_blank"}
- **`ObserverRegistry`** — restricted to `Observer` instances. [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer_registry.py){:target="_blank"}

## Default Registry

*core_lib.registry.default_registry.DefaultRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L4){:target="_blank"}

`DefaultRegistry` implements the `Registry` interface and provides the common behavior used by `CacheRegistry`, `ObserverRegistry`, and connection registries.

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
from core_lib.registry.default_registry import DefaultRegistry

registry_factory.get('user_name')
```



#### register()

*core_lib.registry.default_registry.DefaultRegistry.register()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L12){:target="_blank"}

Registers the key and value into the registry.

```python
def register(self, key: str, object, is_default: bool = False):
    ...
```

**Arguments**

- **`key`** *`(str)`*: A unique string to identify the registered object; duplicate keys are not allowed and will raise a `ValueError`.
- **`object`**: Value to store under the key.
- **`is_default`** *`(bool)`*: When multiple entries are registered, set `is_default=True` to mark this entry as the default. `get()` with no `key` returns the default.

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

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/core_lib_main_class.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/result_to_dict.html">Next</a></button>
</div>
