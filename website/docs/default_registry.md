---
id: default_registry
title: Default Registry
sidebar_label: Default Registry
---
## Default Registry
`Core-Lib` provides a `DefaultRegistry` where users can register different types of datatypes and values corresponding to those datatypes.


Functions provided by the `DefaultRegistry` are as follows:

- `register()`: Register's the name and value into the registry.
````python
def register(self, name: str, object, is_default: bool = False):
    assert name and object
    if not isinstance(object, self._object_type):
        raise ValueError("register object is not of type \"{}\"".format(self._object_type))

    if name in self.name_to_object:
        raise ValueError("cache by name \"{}\" already registerd for type \"{}\"".format(name, object.__class__))

    if is_default:
        self.default_name = name
    self.name_to_object[name] = object
````
`name` is type `str`, sets the name of the registry entry passed to the function.

`object` is the actual data to be passed to the function to store in registry.

`is_default` is type `bool`, for multiple entries in a same registry `is_default` can be used to set the default value to be
returned by the `get` function.



- `unregister()`: Unregisters/removes an entry present in the registry.
```python
def unregister(self, name: str):
    if name in self.name_to_object:
        del self.name_to_object[name]
        if self.default_name == name:
            self.default_name = None
```
`name` is type `str`, is the name of the entry to be unregistered from the registry.
>If `name` is not specified when executing `unregister()`, the default value will be unregistered from the registry.



- `get()`: Returns an entry from the registry with the specified name.

```python
def get(self, name: str = None, *args, **kwargs):
    result = self.name_to_object.get(name or self.default_name)
    if not name and not result and len(self.name_to_object) > 0:
        result = list(self.name_to_object.values())[0]
    return result
```

`name` is type `str`, is the name of the registry entry to be returned.
>If `get()` is used without any parameters, it will return the default value supplied by the user, or the 
>first entry in the registry if the default value also isn't provided.



- `registered()`: Returns all the registered entities in the registry in the type `list`.

```python
def registered(self):
    return list(self.name_to_object.keys())
```

### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

# Single Entry
string = 'hello world'
# initialize and provide data type to the registry
registry_factory = DefaultRegistry(str) 
registry_factory.register('string', string)

data_from_registry = registry_factory.get('string')
print(data_from_registry)  # "hello world"

# Unregister 'string' from registry
registry_factory.unregister('string')

data_from_registry = registry_factory.get('string')
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