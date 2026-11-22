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

### `cache_example.py`

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

  `some_key{param_1}{param_2}`: Build a key with the `param_1` and `param_2` values. A parameter whose value is falsy (`0`, `None`, `''`, `False`, `[]`) renders as `!E<name>E!`, and a placeholder naming no parameter renders as `!M<name>M!`.
  
- **`max_key_length`** *`(int)`*: Default `250`, the maximum length of key string to be accepted by decorator.

- **`expire`** *`(timedelta/string)`*: Default `None`, Period of time when the value is expired. `None` keeps the value until it is invalidated. A string (`'1 hour'`) is parsed once, when the function is decorated, to exactly the time written. Each handler keeps its backend's precision and refuses finer: RAM any length, Redis whole milliseconds, memcached whole seconds. An `expire` of zero or less raises `ValueError` on the RAM, Redis and memcached handlers. An `expire` the handler cannot keep exactly raises `ValueError` on the store, because the cache never changes the time a caller chose.

- **`invalidate`** *`(bool)`*: Default `False`, Remove the value from the cache using the key.

- **`handler_name`** *`(str)`*: Default `None`, The key of `CacheHandler` that registered into the `CoreLib.cache_registry`.

- **`cache_empty_result`** *`(bool)`*: Default `True`, when `True`, will cache empty values as `{}`, `[]`, `""` and `0`.

**Warning: two different calls can share one cached value.** The key is the only thing that tells cached results apart, and `@Cache` shapes it before any handler sees it:

- spaces become `_`, so `'acme widget'` and `'acme_widget'` share one entry;
- line breaks (`\n`, `\r`) are removed;
- the key is cut to `max_key_length` characters, so two keys alike up to that length share one entry;
- every falsy argument renders as the same `!E<name>E!`, so `get(0)` and `get(None)` share one entry.

A call that shares an entry gets the other call's result. Build keys from ids and short codes, never from free text (names, emails, search terms), and keep them under the limit.

### What every handler does the same, and what each backend adds

The RAM, Redis and memcached handlers behave the same where it matters:

- **Wrong data raises; it is never changed to fit.** A key, value or `expire` a handler cannot keep exactly as given raises. The cache never rewrites a key, rounds an expire or converts a value.
- **A store that fails raises and changes nothing.** Whatever the reason (a refused key, value or `expire`, a value over the backend's size limit, a server that cannot be reached), `set` raises, and any older value under the key stays.
- **An unreachable server never takes a store:** `set` raises on Redis and memcached alike. Reads and deletes follow the backend's own client (table below).
- **An `expire` of zero or less raises `ValueError`**, and an expired value is gone, on every handler.
- **Nothing is caught for you:** no fallback to "uncached", no retry, no deleting a key behind your back. What to do when the cache refuses a value or fails is the caller's decision.

No handler is limited to what another can do. Each takes everything its backend can keep:

| | RAM | Redis | memcached |
|---|---|---|---|
| Key | any `str` | any `str` (Redis keys are binary-safe, up to 512 MB) | not empty, at most 250 **bytes**, no space or control character; any other raises python-memcached's `MemcachedKeyError` on `get`, `set` and `delete` |
| Value | any object, kept as given | `dict`, `list`, `int` or `str`, kept as JSON; anything else raises `ValueError` | as Redis |
| `expire` | any length | whole milliseconds | whole seconds |
| One value's size | no limit | 512 MB | 1 MB (raises `RuntimeError`) |
| Server down | - | every operation raises `redis.exceptions.ConnectionError` | `set` raises `RuntimeError`; python-memcached raises nothing for the rest: `get` answers a miss, `delete` and `flush_all` do nothing |

So code that runs on one handler can be refused by another: a key with a space works on Redis and RAM but raises on memcached, and a 500 ms `expire` works on RAM and Redis but raises on memcached. Test with the handler production uses. A non-ASCII character takes 2 to 4 bytes, so a key within `max_key_length`'s 250 characters can be over memcached's 250 bytes.

What a hit returns differs the same way: Redis and memcached keep JSON, so a hit is a fresh copy, a dict's int keys come back as strings, a tuple inside the value comes back as a list, and a value holding something JSON cannot encode (a `set`, a `datetime` inside it) raises `TypeError` on the store. The RAM handler returns the object itself, as given.



### CacheHandler

*core_lib.cache.cache_handler.CacheHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler.py#L5){:target="_blank"}

`CacheHandler` is an empty base abstract class with `get`, `set`, `delete`, and `flush_all` operations. You can implement it to support any caching service  

By default, `Core-Lib` provides four built-in `CacheHandler` implementations, all behaving as above. A handler of your own should too: raise for what its backend cannot keep exactly (`core_lib/cache/cache_helpers.py` has the checks the handlers share).

1. `core_lib.cache.cache_handler_ram.CacheHandlerRam` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_ram.py){:target="_blank"}

   Cache data inside the memory of the running process; it is gone when the process ends. It keeps any key and the value object itself, with an `expire` of any length; an expired value is dropped when it is next read.

2. `core_lib.cache.cache_handler_memcached.CacheHandlerMemcached` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_memcached.py){:target="_blank"}

   Cache data inside [memcached](https://memcached.org){:target="_blank"} server

   - An `expire` over 30 days is sent as the equivalent Unix time, the form memcached requires for it, so it lasts exactly as long as asked. memcached reads that time against its **own** clock: keep the server's clock in step with the clients' (NTP), or such a value lives longer or shorter by the difference.
   - A store memcached does not make (a value over its 1 MB item limit, or the server unreachable) raises `RuntimeError`.
   - Keys and `expire` as in the table above: memcached's own key limits, and whole seconds.
   - memcached's clock ticks once a second, so a value with an `expire` of N seconds lives between N-1 and N seconds.

3. `core_lib.cache.cache_handler_redis.CacheHandlerRedis` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_redis.py){:target="_blank"}

   Cache data inside [redis](https://redis.io){:target="_blank"} server

   - Any key, and an `expire` to the millisecond (sent as `PX`).
   - An unreachable server raises `redis.exceptions.ConnectionError`.
   - `flush_all` sends `FLUSHALL`, which empties **every database** of the Redis server, not only the handler's own: never share the cache's Redis with other data.

4. `core_lib.cache.cache_handler_no_cache.CacheHandlerNoCache` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_no_cache.py){:target="_blank"}

   Keeps nothing and checks nothing: every `get` is a miss.

**Note:** `CacheHandlerMemcached` and `CacheHandlerRedis` support only `dict`, `list`, `int` and `str` values (any other value raises `ValueError`). To cache an entity or any other data type on them, put the `@ResultToDict` decorator under the `@Cache` decorator. Example:

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

### `demo_core_lib.py`

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

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/generation.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/job.html">Next >></a></button>
</div>