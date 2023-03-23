---
id: cache
title: Cache
sidebar_label: Cache
---
The `Cache` decorator handles the `get`,` set`, and `delete` cache operations automatically in a single, easy-to-use decorator.


### Example:

##### cache_example.py

```python
CACHE_KEY_FOO = 'test_cache_param_{foo_id}'

# Cache the return value 
@Cache(key=CACHE_KEY_FOO, expire=timedelta(houers=3, minutes=2, seconds=1))
def get_foo(foo_id):
    value = ... # Do some calculation
    return value

# Clear the same cache key CACHE_KEY_FOO` acourding to the invalidate=True parameter
@Cache(key=CACHE_KEY_FOO, invalidate=True)
def set_foo(self, foo_id, foo_value):
    ... # update the value
```



*core_lib.cache.cache_decorator.Cache* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_decorator.py#L34)

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

- **`key`** *`(str)`*:  Default `None`, The key used to store the value. possible values are:
  `None`: the decorated  `function.__qualname__` is used.     

  `some_key{param_1}{param_2}`: Build a key with the `param_1` and `param_2` values. When a parameter is optional or empty _ will be used. 
  
- **`max_key_length`** *`(int)`*: Default `250`, the maximum length of key string to be accepted by decorator.

- **`expire`** *`(timedelta/string)`*: Default `None`, Period of time when the value is expired.

- **`invalidate`** *`(bool)`*: Default `False`, Remove the value from the cache using the key.

- **`handler_name`** *`(str)`*: Default `None`, The key of `CacheHandler` that registered into the `CoreLib.cache_registry`.

- **`cache_empty_result`** *`(bool)`*: Default `True`, when `True`, will cache empty values as `{}`, `[]`, `()`, `""` and `set()`.



### CacheHandler

*core_lib.cache.cache_handler.CacheHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler.py#L5)

`CacheHandler` is an empty base abstract class with `get`, `set`, `delete`, and `flush_all` operations. You can implement it to support any caching service  

By default, `Core-Lib` provides four built-in `CacheHandler` implementations.

1. `core_lib.cache.cache_handler_ram.CacheHandlerRam` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_ram.py#L6)

​		Cache data inside the memory will get invalidated upon the termination of the running process.

2. `core_lib.cache.cache_handler_memcached.CacheHandlerMemcached` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_memcached.py#L8)

   Cache data inside [memcached](https://memcached.org) server

3. `core_lib.cache.cache_handler_redis.CacheHandlerRedis` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_redis.py#L9)

   Cache data inside [redis](https://redis.io) server

4. `core_lib.cache.cache_handler_no_cache.CacheHandlerNoCache` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_no_cache.py#L9)

​		A dummy class, without implementation, used for testing purposes

**Note:** `CacheHandlerMemcached` and `CacheHandlerRedis` will support only `dict` and  `list` data types. To cache any other data type, use the `@ResultToDict` decorator before the `@Cache` decorator. Example:

```python
@Cache(CACHE_SOME_KEY)
@ResultToDict()
def action(self):
  ...
```




### CacheRegistry

*core_lib.cache.cache_registry.CacheRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py#L5)

The `Cache` decorator uses of `CoreLib`'s `CacheRegistry` to fetch the correct `CacheHandler`. So before using the `Cache` decorator, we must register our `CacheHandler` of choice inside the CoreLib `CacheRegistry.`
By default `CoreLib` class already comes with a predefined static instance of the `CacheRegistry`

The `Cache` decorator knows what `CacheHandler` to get by the `handler_name` parameter. If `handler_hanler` is neglected, the CacheRegistry will return the default `CacheHandler`

##### example.py

```python
from core_lib.cache.cache_registry import CacheRegistry
from core_lib.cache.cache_handler_ram import CacheHandlerRam

cache_registry = CacheRegistry()
cache_registry.register("mem", CacheHandlerRam())
...
cache_registry.get("mem") # returns `CacheHandlerRam`
cache_registry.get() # returns single/default `CacheHandlerRam`. //See DefaultRegistry documentation

cache_registry.register("mem2", CacheHandlerRam())
cache_registry.get() # returns None. Multiple client registered with no default
```



##### demo_core_lib.py

```python
from memcache import Client
...

class DemoCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        cache_client_memcached = CacheHandlerMemcached(build_url(**self.config.memcached))
        cache_registry = CacheRegistry()
        cache_registry.register("memcached", cache_client_memcached)
        ...
```

