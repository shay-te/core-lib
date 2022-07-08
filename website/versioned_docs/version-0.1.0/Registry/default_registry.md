---
id: default_registry
title: Default Registry
sidebar_label: Default Registry
---
## Default Registry

*core_lib.registry.default_registry.DefaultRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L4)

`Core-Lib` provides a `DefaultRegistry` where users can register different types of datatypes and values corresponding to those datatypes.

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
from core_lib.registry.default_registry import DefaultRegistry

.
.
.
registry_factory.unregister('user_name')
```

### get()

*core_lib.registry.default_registry.DefaultRegistry.get()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L30)

Returns an entry from the registry with the specified key.

```python
def get(self, key: str = None, *args, **kwargs):
    ...
```
**Arguments**

- **`key`** *`(str)`*: Is the key of the registry entry to be returned.

>If `get()` is used without any parameters, it will return the default value supplied by the user, or the 
>first entry in the registry if the default value also isn't provided. 

>If the registry is empty or the `get()` is called with a `key` that does not exist in the registry it will return
> `None`


#### Usage
```python
from core_lib.registry.default_registry import DefaultRegistry

.
.
.
registry_factory.get('user_name')
```
### registered()

*core_lib.registry.default_registry.DefaultRegistry.registered()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/registry/default_registry.py#L36)

Returns all the registered entities in the registry in the type `list`.

```python
def registered(self):
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
