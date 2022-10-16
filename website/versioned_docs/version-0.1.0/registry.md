---
id: registry
title: Registry
sidebar_label: Registry
---
`Registry` Provide base class for a simple `Registry pattern` with single abstract `get` function. 
It being use by the `CacheRegistry`,  `ConnectionRegistry` and more...

## Registry

*core_lib.registry.Registry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/registry.py)

By default, `Core-Lib` provides three `Registry` implementations.   

1. `core_lib.registry.default_registry.DefaultRegistry` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py)
2. `core_lib.connection.connection_registry.ConnectionRegistry` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/connection/connection_registry.py)
3. `core_lib.cache.cache_registry.CacheRegistry` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py)
4. `core_lib.observer.observer_registry.ObserverRegistry` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer_registry.py)



## Default Registry

*core_lib.registry.default_registry.DefaultRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L4)

 `DefaultRegistry` is impletemeting the `Registry` abstract class and provide boilerplate baseclass. 
it is being used by `CacheRegistry`, `ObserverRegistry` and more.

The `DefaultRegistry` constructor:

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

*core_lib.registry.default_registry.DefaultRegistry.get()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L30)

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

*core_lib.registry.default_registry.DefaultRegistry.register()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L12)

Register's the key and value into the registry.

````python
def register(self, key: str, object, is_default: bool = False):
    ...
````

**Arguments**

- **`key`** *`(str)`*: Sets the key of the registry entry passed to the function, registering the same key again will raise an `ValueError`.
- **`object`**: Is the actual data to be passed to the function to store in registry.
- **`is_default`** *`(bool)`*: For multiple entries in a same registry `is_default` can be used to set the default value to be
returned by the `get` function when calling it without parameters.

#### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

user_name = 'Jon Doe'
registry_factory = DefaultRegistry(str) 
registry_factory.register('user_name', user_name)
```



### unregister()

*core_lib.registry.default_registry.DefaultRegistry.unregister()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L24)

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

*core_lib.registry.default_registry.DefaultRegistry.registered()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L36)

Returns all the registered entities in the registry in the type `list`.

```python
def registered(self):
```

```python
registry_factory.registered()
```

