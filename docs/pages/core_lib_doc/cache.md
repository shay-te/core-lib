---
id: cache
title: Cache
sidebar: core_lib_doc_sidebar
permalink: cache.html
folder: core_lib_doc
toc: false
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
#### Code Explained:
- **`CACHE_KEY_FOO`**: This variable holds a string representing the cache key format. It contains a placeholder {foo_id} which will be replaced with the actual foo_id value.

- **`@Cache`**: This is a decorator function used for caching. It takes parameters such as key, expire, and invalidate. The key parameter specifies the cache key format, expire specifies the expiration time for cached values, and invalidate is a flag indicating whether to invalidate the cache.

- **`get_foo`**: This function is decorated with @Cache. It computes a value based on foo_id and returns it. The decorator caches the return value of this function using the specified cache key and expiration time.

- **`set_foo`**: This function is also decorated with @Cache. It is responsible for updating the value associated with a given foo_id. When invalidate=True, it indicates that the cache for the specified key (CACHE_KEY_FOO) should be cleared, ensuring that the next call to get_foo retrieves the updated value.
<br>
<br>
<br>

*core_lib.cache.cache_decorator.Cache* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_decorator.py#L34){:target="_blank"}

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

*core_lib.cache.cache_handler.CacheHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler.py#L5){:target="_blank"}

`CacheHandler` is an empty base abstract class with `get`, `set`, `delete`, and `flush_all` operations. You can implement it to support any caching service  

By default, `Core-Lib` provides four built-in `CacheHandler` implementations.

1. `core_lib.cache.cache_handler_ram.CacheHandlerRam` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_ram.py#L6){:target="_blank"}

​		Cache data inside the memory will get invalidated upon the termination of the running process.

2. `core_lib.cache.cache_handler_memcached.CacheHandlerMemcached` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_memcached.py#L8){:target="_blank"}

   Cache data inside [memcached](https://memcached.org){:target="_blank"} server

3. `core_lib.cache.cache_handler_redis.CacheHandlerRedis` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_redis.py#L9){:target="_blank"}

   Cache data inside [redis](https://redis.io){:target="_blank"} server

4. `core_lib.cache.cache_handler_no_cache.CacheHandlerNoCache` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_no_cache.py#L9){:target="_blank"}

​		A dummy class, without implementation, used for testing purposes

**Note:** `CacheHandlerMemcached` and `CacheHandlerRedis` will support only `dict` and  `list` data types. To cache any other data type, use the `@ResultToDict` decorator before the `@Cache` decorator. Example:

```python
@Cache(CACHE_SOME_KEY)
@ResultToDict()
def action(self):
  ...
```




### CacheRegistry

*core_lib.cache.cache_registry.CacheRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py#L5){:target="_blank"}

The `Cache` decorator uses `CoreLib's` `CacheRegistry` to fetch the correct `CacheHandler`. So before using the `Cache` decorator, we must register our `CacheHandler` of choice inside the CoreLib `CacheRegistry.`
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

- **`Cache Registry Initialization`**: An instance of CacheRegistry is created (`cache_registry`). This registry is intended to hold references to different cache handlers.

- **`Cache Handler Registration`**: A cache handler is registered with a specific key ("mem") using `cache_registry`.`register("mem", CacheHandlerRam()`). This associates the key "mem" with a `CacheHandlerRam` instance.

- **`Retrieving Cache Handlers`**:

    - **`cache_registry.get("mem")`**: Returns the cache handler associated with the key "mem", which is an instance of CacheHandlerRam.
    - **`cache_registry.get()`**: Returns the default cache handler. However, in the code snippet, there is no default specified, so it might return None or a predefined default if set elsewhere.
    - **`cache_registry.get("mem2")`**: Returns the cache handler associated with the key "mem2" if it were registered.
    - **`Multiple Registrations`**: Another cache handler is registered with the key "mem2" using `cache_registry.register`(`"mem2", CacheHandlerRam()`). This allows for multiple cache handlers to be registered within the same `CacheRegistry` instance.

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

- **`Class Definition`**: DemoCoreLib is defined, and it seems to inherit from CoreLib (assuming CoreLib is a pre-existing class).

 - **`Constructor`**: The `__init__` method is defined to initialize instances of DemoCoreLib. It takes a configuration dictionary (conf) as input.

- **`Configuration Handling`**: The configuration dictionary is stored as an attribute `(self.config)` of the DemoCoreLib instance.

- **`Cache Initialization`**:
    - A `CacheHandlerMemcached` instance (`cache_client_memcached`) is created using the configuration provided in `self.config.memcached`. This suggests that DemoCoreLib utilizes `Memcached `for caching.
    - A CacheRegistry instance (`cache_registry`) is created.
    - The `cache_client_memcached` is registered with the key "memcached" within the `cache_registry`.