---
id: registry
title: Registry
sidebar: core_lib_doc_sidebar
permalink: registry.html
folder: core_lib_doc
toc: false
---
`Registry` provide base class for a simple `Registry pattern` with single abstract `get` function. 
It being use by the `CacheRegistry`,  `ConnectionRegistry` and more...

## Registry

*core_lib.registry.Registry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/registry.py){:target="_blank"}

`Core-Lib`  basic `Registry` class is used by most of `Core-Lib` modules

1. `core_lib.registry.default_registry.DefaultRegistry` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py){:target="_blank"}

   Base basic implementation of the `Registry` class with four basic functions `register`, `unregister`, `get`, `registered`


2. `core_lib.connection.connection_registry.ConnectionRegistry` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/connection/connection_registry.py){:target="_blank"}

​	Extends the `Registry` and a base class for all  `ConnectionRegistry` classes.

3. `core_lib.cache.cache_registry.CacheRegistry` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py){:target="_blank"}

Extends the `DefaultRegistry` and is limited to storing only `CacheHandler` instances using an `object_type` parameter

4. `core_lib.observer.observer_registry.ObserverRegistry` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer_registry.py){:target="_blank"}

Extends the `DefaultRegistry` and is limited to storing only `Observer` instances using an `object_type` parameter



## Default Registry

*core_lib.registry.default_registry.DefaultRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L4){:target="_blank"}

`DefaultRegistry` is implementing the `Registry` abstract class and providing a boilerplate base class for `CacheRegistry`, `ObserverRegistry`, and more.

### Constractor:

```python
class DefaultRegistry(Registry):

    def __init__(self, object_type: object):
        ...
```

**Arguments**

- **`object_type`** *`(object)`*: Datatype of the object that is to be stored in the registry.

#### Usage

```python
from core_lib.registry.default_registry import DefaultRegistry

class Customer(object):
    ...
        
class CustomerRegistry(DefaultRegistry):

    def __init__(self):
        DefaultRegistry.__init__(self, Customer)
```


### Functions:

### get()

*core_lib.registry.default_registry.DefaultRegistry.get()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L30){:target="_blank"}

Returns an fresh entry from the registry with the specified key.

```python
def get(self, key: str = None, *args, **kwargs):
    ...
```

**Arguments**

- **`key`** *`(str)`*: Is the key of the registry entry to be returned.



>If `get()` is used without any parameters, it will return the default value supplied by the user, or the 
>first entry in the registry if the default value also isn't provided. 

>If the registry is empty or the `get()` is called with a `key` that does not exist in the registry it will return
>`None`



#### Usage

```python
from core_lib.registry.default_registry import DefaultRegistry

registry_factory.get('user_name')
```



### register()

*core_lib.registry.default_registry.DefaultRegistry.register()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L12){:target="_blank"}

Register's the key and value into the registry.

````python
def register(self, key: str, object, is_default: bool = False):
    ...
````

**Arguments**

- **`key`** *`(str)`*: A unique string to identify the registered object; duplicate key's are not allowed and will cause an `ValueError`.
- **`object`**: Any value we wish to store with the attached key
- **`is_default`** *`(bool)`*: For multiple entries in a same registry `is_default` can be used to set the default value to  mark this object as default, default value can be fetched when calling `get` without a `key` parameter.

#### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

user_name = 'Jon Doe'
registry_factory = DefaultRegistry(str) 
registry_factory.register('user_name', user_name)
```



### unregister()

*core_lib.registry.default_registry.DefaultRegistry.unregister()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L24){:target="_blank"}

Unregisters/removes an entry present in the registry.

```python
def unregister(self, key: str):
    ...
```
**Arguments**

- **`key`** *`(str)`*: Is the key of the entry to be unregistered from the registry.


>The first item in the registry becomes default when we unregister a default `key`.


#### Usage
```python
registry_factory.unregister('user_name')
```



### registered()

*core_lib.registry.default_registry.DefaultRegistry.registered()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L36){:target="_blank"}

Returns all the registered entities in the registry in the type `list`.

```python
def registered(self):
```

#### Usage

```python
registry_factory.registered()
```

