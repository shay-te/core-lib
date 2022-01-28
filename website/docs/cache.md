---
id: cache
title: Cache
sidebar_label: Cache
---

`Core-Lib` provide plug-able cache functionalists that can be extended. And used as a decorator and as an instance.

## CacheHandler

`CacheHandler` base class provides the basic API functions used by `Core-Lib`.

```python
class CacheHandler(ABC):

    # Fetch data from the cache using the `key`, returns None when no value was found
    @abstractmethod
    def get(self, key):
        pass

    # Store the `value` to cache by the `key`.
    # None `expire` will tell the storage to hold the value "forever" or after the designated period expires
    @abstractmethod
    def set(self, key: str, value, expire: timedelta):
        pass

    # Remove the value from the cache using the `key`
    @abstractmethod
    def delete(self, key: str):
        pass
```

By default `Core-Lib` provides two `CacheHandler` implementation.   
1. `core_lib.cache.cache_client_ram.CacheHandlerRam`
2. `core_lib.cache.cache_client_memcached.CacheHandlerMemcached`


## CacheClientFactory

`CacheClientFactory` class holds all instances of `CacheHandler` classes and provides two main functions.

```python
from core_lib.cache.cache_client_factory import CacheClientFactory
from core_lib.cache.cache_handler_ram import CacheHandlerRam

cache_client_factory = CacheClientFactory()
cache_client_factory.register("mem", CacheHandlerRam())
...
cache_client_factory.get("mem") # returns registered `CacheHandlerRam`
cache_client_factory.get() # returns registered `CacheHandlerRam`. Only when a single client is registered, 

cache_client_factory.register("mem2", CacheHandlerRam())
cache_client_factory.get() # returns None. Multiple client registered.
``` 


## Cache

`Cache` decorator. cache's the return value of the decorated method. And accept the following parameters.

```python
class Cache(object):
    ...
    def __init__(self, key: str = None, expire: timedelta = None, invalidate: bool = False, cache_client_name: str = None):
```
* `key` The key used to store the value. possible values are:
   
    `None`: the decorated  `function.__qualname__` is used.     
    
    `some_key{param_1}{param_2}`: will build a key with the `param_1` and `param_2` values.     
    when a parameter is optional and empty `_` is used. 
* `expire` Period of time when the value is expired.
* `invalidate` Remove the value from the cache using the key.
* `cache_client_name` The name to pay to get the correct `CacheHandler`.


### Cache Initialization

The `Cache` decorator is using the `CacheClientFactory` to get the designated `CacheHandler`   
Initializing `Core-Lib` with `Cache` example: 

```python
from memcache import Client
...

class DemoCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        cache_client_memcached = CacheHandlerMemcached(Client([build_url(**self.config.memcached)]))
        cache_factory = CacheClientFactory()
        cache_factory.register("memcached", cache_client_memcached)
        Cache.set_cache_factory(cache_factory)
        ...
``` 

### Using The Cache decorator.

```python

# return cached value or generate result and store in cache
@Cache(key="test_cache_param_{foo_id}", expire=timedelta(houers=3, minutes=2, seconds=1))
def get_foo(foo_id):
    value = ... # Do some calculation
    return value

# Clear the cache 
@Cache(key="test_cache_param_{foo_id}", invalidate=True)
def set_foo(self, foo_id, foo_value):
    ... # update the value

```
 
