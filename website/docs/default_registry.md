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

class Customer(object):
    ...
        
        
class CustomerRegistry(DefaultRegistry):

    def __init__(self):
        DefaultRegistry.__init__(self, Customer)
        
# Single Entry
customer =  Customer()
# initialize the registry
customer_registry = CustomerRegistry()
customer_registry.register('customer_a', customer)

# Get Customer data
customer_data = customer_registry.get('customer_a') 
print(customer_data) # customer_a data 

# Unregister 'customer_a' from registry
customer_registry.unregister('customer_a')

customer_data = customer_registry.get('customer_a') 
print(customer_data) # customer_a data # None 


# Multiple Entries
customer_a =  Customer()
customer_b =  Customer()
customer_registry = CustomerRegistry()
customer_registry.register('customer_a', customer_a)
customer_registry.register('customer_b', customer_b, is_default=True)

customer_data = customer_registry.get() 
print(customer_data) # customer_b data

customer_data = customer_registry.get('customer_a') 
print(customer_data) # customer_a data

registered_list = customer_registry.registered() 
print(registered_list) # ['customer_a', 'customer_b']

# Unregister customer_a from registry
customer_registry.unregister('customer_a')

registered_list = customer_registry.registered() 
print(registered_list) # ['customer_b']

# Unregister everything from registry
customer_registry.unregister()

registered_list = customer_registry.registered() 
print(registered_list) # None
```