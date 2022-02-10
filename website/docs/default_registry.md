---
id: default_registry
title: Default Registry
sidebar_label: Default Registry
---
## Default Registry
`Core-Lib` provides a `DefaultRegistry` where users can register different types of datatypes and values corresponding to those datatypes.

The `DefaultRegistry` constructor:
```python
class DefaultRegistry(Registry):

    def __init__(self, object_type: object):
        ...
```
`object_type`: Datatype of the object that is to be stored in the registry.

#### Usage

```python
from core_lib.registry.default_registry import DefaultRegistry

# Registry that will only accept type string 
registry_factory = DefaultRegistry(str) 
```



Functions provided by the `DefaultRegistry` are as follows:

- `register()`: Register's the key and value into the registry.
````python
def register(self, key: str, object, is_default: bool = False):
    ...
````
`key` is type `str`, sets the key of the registry entry passed to the function.

`object` is the actual data to be passed to the function to store in registry.

`is_default` is type `bool`, for multiple entries in a same registry `is_default` can be used to set the default value to be
returned by the `get` function when calling it without parameters.

#### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

user_name = 'Jon Doe'
registry_factory = DefaultRegistry(str) 
registry_factory.register('user_name', user_name)
```



- `unregister()`: Unregisters/removes an entry present in the registry.
```python
def unregister(self, key: str):
    ...
```
`key` is type `str`, is the key of the entry to be unregistered from the registry.
>If `key` is not specified when executing `unregister()`, the default value will be unregistered from the registry.

#### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

.
.
.
registry_factory.unregister('user_name')
```



- `get()`: Returns an entry from the registry with the specified key.

```python
def get(self, key: str = None, *args, **kwargs):
    ...
```

`key` is type `str`, is the key of the registry entry to be returned.
>If `get()` is used without any parameters, it will return the default value supplied by the user, or the 
>first entry in the registry if the default value also isn't provided.

#### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

.
.
.
registry_factory.get('user_name')
```


- `registered()`: Returns all the registered entities in the registry in the type `list`.

```python
def registered(self):
    return list(self.key_to_object.keys())
```

#### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

.
.
.
registry_factory.registered()
```

### Example of DefaultRegistry
```python
from core_lib.registry.default_registry import DefaultRegistry

# Single Entry
user_name = 'Jon Doe'
# initialize and provide data type to the registry
registry_factory = DefaultRegistry(str) 
registry_factory.register('user_name', user_name)

data_from_registry = registry_factory.get('user_name')
print(data_from_registry)  # "Jon Doe"

# Unregister 'string' from registry
registry_factory.unregister('user_name')

data_from_registry = registry_factory.get('user_name')
print(data_from_registry)  # None

# Multiple Entries
registry_factory = DefaultRegistry(str) 

string_1 = 'this is normal entry'
registry_factory.register('string_1', string_1)

string_2 = 'this is default entry'
# set this entry as default
registry_factory.register('string_2', string_2, is_default=True)

data_from_registry = registry_factory.get()
print(data_from_registry)  # "this is default entry"

data_from_registry = registry_factory.get('string_1')
print(data_from_registry)  # "this is normal entry"

registered_list = registry_factory.registered()
print(registered_list)  # ['string_1', 'string_2']

# Unregister string_1 from registry
registry_factory.unregister('string_1')

registered_list = registry_factory.registered()
print(registered_list)  # ['string_2']

# Unregister everything from registry
registry_factory.unregister()

registered_list = registry_factory.registered()
print(registered_list)  # None
```