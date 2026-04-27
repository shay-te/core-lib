---
id: cache
title: Cache
sidebar: core_lib_doc_sidebar
permalink: cache.html
folder: core_lib_doc
toc: false
---

Without a caching layer, expensive queries run on every request. Without a cache-invalidation layer, stale data stays in memory after updates. The `@Cache` decorator handles both in one place — get, set, and delete — so you don't scatter cache logic across your service methods.

### Example

```python
CACHE_KEY_FOO = 'test_cache_param_{foo_id}'

# Cache the return value
@Cache(key=CACHE_KEY_FOO, expire=timedelta(hours=3, minutes=2, seconds=1))
def get_foo(foo_id):
    value = ...  # expensive computation
    return value

# Invalidate the same key on write
@Cache(key=CACHE_KEY_FOO, invalidate=True)
def set_foo(self, foo_id, foo_value):
    ...  # update the value
```

---

*core_lib.cache.cache_decorator.Cache* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_decorator.py#L34){:target="_blank"}

```python
class Cache(object):
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

- **`key`** *`(str)`*: Default `None` — uses `function.__qualname__`. Supports parameter interpolation: `'user_{user_id}'` builds a per-user key.
- **`max_key_length`** *`(int)`*: Default `250` — maximum allowed key length.
- **`expire`** *`(timedelta/str)`*: Default `None` — how long before the cached value expires.
- **`invalidate`** *`(bool)`*: Default `False` — when `True`, deletes the cached value instead of reading it.
- **`handler_name`** *`(str)`*: Default `None` — which `CacheHandler` to use from the `CacheRegistry`.
- **`cache_empty_result`** *`(bool)`*: Default `True` — when `True`, caches empty values (`{}`, `[]`, `()`, `""`, `set()`).

---

### CacheHandler

*core_lib.cache.cache_handler.CacheHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler.py#L5){:target="_blank"}

`CacheHandler` is an abstract base class with `get`, `set`, `delete`, and `flush_all` operations. Implement it to support any caching backend.

Core-Lib provides four built-in implementations:

1. `core_lib.cache.cache_handler_ram.CacheHandlerRam` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_ram.py#L6){:target="_blank"} — in-memory cache, cleared when the process stops.

2. `core_lib.cache.cache_handler_memcached.CacheHandlerMemcached` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_memcached.py#L8){:target="_blank"} — [Memcached](https://memcached.org){:target="_blank"} backend.

3. `core_lib.cache.cache_handler_redis.CacheHandlerRedis` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_redis.py#L9){:target="_blank"} — [Redis](https://redis.io){:target="_blank"} backend.

4. `core_lib.cache.cache_handler_no_cache.CacheHandlerNoCache` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_no_cache.py#L9){:target="_blank"} — no-op implementation for tests.

> `CacheHandlerMemcached` and `CacheHandlerRedis` support `dict`, `list`, `int`, and `str`. To cache other types (e.g. SQLAlchemy model objects), apply `@ResultToDict()` before `@Cache`:
> ```python
> @Cache(CACHE_SOME_KEY)
> @ResultToDict()
> def action(self):
>     ...
> ```

---

### CacheRegistry

*core_lib.cache.cache_registry.CacheRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py#L5){:target="_blank"}

The `@Cache` decorator looks up the correct `CacheHandler` from `CoreLib`'s `CacheRegistry`. Register your handler before using the decorator.

```python
from core_lib.cache.cache_registry import CacheRegistry
from core_lib.cache.cache_handler_ram import CacheHandlerRam

cache_registry = CacheRegistry()
cache_registry.register("mem", CacheHandlerRam())

cache_registry.get("mem")  # returns CacheHandlerRam
cache_registry.get()       # returns the single/default handler

cache_registry.register("mem2", CacheHandlerRam())
cache_registry.get()       # returns None — multiple handlers, no default set
```

**Wiring in your `CoreLib`:**

```python
class YourCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        super().__init__()
        cache_client = CacheHandlerMemcached(build_url(**conf.memcached))
        CoreLib.cache_registry.register("memcached", cache_client)
        ...
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/generation.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/job.html">Next >></a></button>
</div>
