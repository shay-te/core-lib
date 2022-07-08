---
id: cache
title: Cache
sidebar_label: Cache
---

`Core-Lib` provide plug-able cache functionalists that can be extended. And used as a decorator and as an instance.

## CacheHandler

*core_lib.cache.cache_handler.CacheHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler.py#L5)

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

By default, `Core-Lib` provides three `CacheHandler` implementations.   
1. `core_lib.cache.cache_client_ram.CacheHandlerRam` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_ram.py#L6)
2. `core_lib.cache.cache_client_memcached.CacheHandlerMemcached` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_memcached.py#L8)
3. `core_lib.cache.cache_client_memcached.CacheHandlerMemcached` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_redis.py#L9)


## CacheRegistry

*core_lib.cache.cache_registry.CacheRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py#L5)

`CacheRegistry` class holds all instances of `CacheHandler` classes and provides two main functions.

```python
from core_lib.cache.cache_registry import CacheRegistry
from core_lib.cache.cache_handler_ram import CacheHandlerRam

cache_registry = CacheRegistry()
cache_registry.register("mem", CacheHandlerRam())
...
cache_registry.get("mem") # returns registered `CacheHandlerRam`
cache_registry.get() # returns registered `CacheHandlerRam`. Only when a single client is registered, 

cache_registry.register("mem2", CacheHandlerRam())
cache_registry.get() # returns None. Multiple client registered.
``` 


## Cache

*core_lib.cache.cache_decorator.Cache* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_decorator.py#L34)

`Cache` decorator. cache's the return value of the decorated method. And accept the following parameters.

```python
class Cache(object):
    ...
    def __init__(
        self,
        key: str = None,
        max_key_length: int = 250,
        expire: Union[timedelta, str] = None,
        invalidate: bool = False,
        handler_name: str = None,
        cache_empty_result: bool = True,
    ):
```
**Arguments**

- **`key`** *`(str)`*: The key used to store the value. possible values are:
    `None`: the decorated  `function.__qualname__` is used.     
    
    `some_key{param_1}{param_2}`: will build a key with the `param_1` and `param_2` values.     
    when a parameter is optional and empty `_` is used. 
- **`max_key_length`** *`(int)`*: Default `250`, the maximum length of key string to be accepted by decorator.
- **`expire`** *`(timedelta)`*: Period of time when the value is expired.
- **`invalidate`** *`(bool)`*: Remove the value from the cache using the key.
- **`handler_name`** *`(str)`*: Name of the handler, will specify what `CacheHandler` to use, using the `CoreLib.cache_registry`.
- **`cache_empty_result`** *`(bool)`*: Default `True`, when `True`, will cache empty values as `{}`, `[]`, `()`, `""` and `set()`.

## Cache Initialization

The `Cache` decorator is using the `CacheRegistry` to get the designated `CacheHandler`   
Initializing `Core-Lib` with `Cache` example: 

```python
from memcache import Client
...

class DemoCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        cache_client_memcached = CacheHandlerMemcached(Client([build_url(**self.config.memcached)]))
        cache_registry = CacheRegistry()
        cache_registry.register("memcached", cache_client_memcached)
        ...
``` 

## Using The Cache decorator.

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
 
