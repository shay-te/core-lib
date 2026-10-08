---
id: cache
title: Cache
sidebar: core_lib_doc_sidebar
permalink: cache.html
folder: core_lib_doc
toc: false
---

`@Cache` stores a method's return value under a key built from the method's arguments. Put `@Cache(..., invalidate=True)` with the same key on the method that changes the data, and that method deletes the stored value after it runs. The storage (process memory, Memcached or Redis) is a cache handler you register once in your `CoreLib`. Switching storage does not change the decorated service code, as long as that code follows the [Memcached and Redis limits](#cachehandler): cached methods return a `dict`, `list`, `int` or `str`, and set `expire` when the storage is Redis. The in-memory handler accepts any value and no `expire`, so code that works on it can fail on Memcached or Redis.

**What it adds** over `functools.lru_cache`: keys you can delete from another method, expiry, and shared storage (Memcached, Redis) that several processes can read. **What it is not:** there is no lock, so two processes that miss the same key both run the method.

> **Where it fits:** Service-layer helper. Apply `@Cache` to a Service method to store its return value; apply `@Cache(..., invalidate=True)` to the matching write method to delete it.

## Example

```python
from datetime import timedelta

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_layers.service.service import Service

SHOP_CORE_LIB_CACHE = 'shop_core_lib'
CACHE_KEY_PRICE = 'shop_price_{product_id}'


class PriceService(Service):
    def __init__(self):
        self._prices = {1: 10}  # stands in for a DataAccess

    @Cache(CACHE_KEY_PRICE, expire=timedelta(minutes=10), handler_name=SHOP_CORE_LIB_CACHE)
    def get(self, product_id: int) -> int:
        print(f'loading price of product {product_id}')
        return self._prices[product_id]

    @Cache(CACHE_KEY_PRICE, handler_name=SHOP_CORE_LIB_CACHE, invalidate=True)
    def update(self, product_id: int, price: int):
        self._prices[product_id] = price


class ShopCoreLib(CoreLib):
    def __init__(self):
        super().__init__()
        if not CoreLib.cache_registry.get(SHOP_CORE_LIB_CACHE):  # the registry is shared by the whole process
            CoreLib.cache_registry.register(SHOP_CORE_LIB_CACHE, CacheHandlerRam())
        self.price = PriceService()


shop_core_lib = ShopCoreLib()
print(shop_core_lib.price.get(1))
print(shop_core_lib.price.get(1))
shop_core_lib.price.update(1, 12)  # deletes the key 'shop_price_1'
print(shop_core_lib.price.get(1))
```

It prints:

```text
loading price of product 1
10
10
loading price of product 1
12
```

The second `get(1)` came from the cache. `update(1, 12)` deleted `shop_price_1`, so the third call loaded the new price. Code that calls `shop_core_lib.price.get()` does not know a cache exists.

## Choosing the storage in YAML

Build the handler from config with [`instantiate_config`](instantiate_config.html), and the storage becomes a config change. This `ShopCoreLib` replaces the one above; `PriceService` and the two constants stay the same:

```python
from omegaconf import DictConfig

from core_lib.cache.cache_handler import CacheHandler
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config


class ShopCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        if not CoreLib.cache_registry.get(SHOP_CORE_LIB_CACHE):
            cache_handler = instantiate_config(config.core_lib.shop_core_lib.cache, CacheHandler)
            CoreLib.cache_registry.register(SHOP_CORE_LIB_CACHE, cache_handler)
        self.price = PriceService()
```

```yaml
# production
core_lib:
  shop_core_lib:
    cache:
      _target_: core_lib.cache.cache_handler_redis.CacheHandlerRedis
      url: redis://cache.internal:6379/0
```

```yaml
# tests and local development
core_lib:
  shop_core_lib:
    cache:
      _target_: core_lib.cache.cache_handler_ram.CacheHandlerRam
```

For Memcached, use `_target_: core_lib.cache.cache_handler_memcached.CacheHandlerMemcached` with `url: cache.internal:11211` (host and port, no scheme). The second argument of `instantiate_config`, `CacheHandler`, makes it raise a `ValueError` if the YAML names a class that is not a cache handler.

---

*core_lib.cache.cache_decorator.Cache* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_decorator.py#L35){:target="_blank"}

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

- **`key`** *`(str)`*: Default `None`. A template whose `{placeholders}` are filled from the method's arguments by parameter name: `'user_{user_id}'` gives one entry per user. **Without a key, every call shares one entry** (the key is the function's `__qualname__`), so `get_user(2)` returns whatever `get_user(1)` stored. Always pass a key that contains the parameters. An argument that is `None`, `0` or `''` is written as `!E<name>E!`, and a placeholder that names no parameter as `!M<name>M!`, so `get_user(0)` and `get_user(None)` share an entry.
- **`max_key_length`** *`(int)`*: Default `250`. Longer keys are cut to this length, not rejected, so two keys that only differ after that point share an entry.
- **`expire`** *`(timedelta/str)`*: Default `None`, which means no expiry. Either a `timedelta`, or a phrase that [parsedatetime](https://github.com/bear/parsedatetime){:target="_blank"} understands, such as `'10 minutes'`, `'3 hours'` or `'30m'`. A string is turned into a duration once, when the decorator is created. This is not the format jobs use: `'2h30m'` raises `ValueError` when your module is imported.
- **`invalidate`** *`(bool)`*: Default `False`. When `True`, the decorator runs the method first and then deletes the key. If the method raises, the key is kept.
- **`handler_name`** *`(str)`*: Default `None`. The name the handler was registered under in `CoreLib.cache_registry`. With `None`, the default handler is used, or the first one registered if none was marked as default. An unknown name raises `ValueError` when the method is called.
- **`cache_empty_result`** *`(bool)`*: Default `True`, which stores every result except `None`. `False` also skips empty and falsy results (`{}`, `[]`, `''`, `0`). A method that returns `None` is never cached, so it runs on every call.

---

### CacheHandler

*core_lib.cache.cache_handler.CacheHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler.py#L5){:target="_blank"}

`CacheHandler` is an abstract base class with `get`, `set`, `delete`, and `flush_all` operations. Implement it to support any other storage.

Core-Lib provides four implementations:

1. `core_lib.cache.cache_handler_ram.CacheHandlerRam` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_ram.py#L6){:target="_blank"}: a dictionary in the process's memory, emptied when the process stops. Each process has its own.

2. `core_lib.cache.cache_handler_memcached.CacheHandlerMemcached` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_memcached.py#L8){:target="_blank"}: [Memcached](https://memcached.org){:target="_blank"}.

3. `core_lib.cache.cache_handler_redis.CacheHandlerRedis` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_redis.py#L9){:target="_blank"}: [Redis](https://redis.io){:target="_blank"}. Always set `expire` on methods cached in Redis: without it, the handler's Redis `SET` call fails with `invalid expire time in 'set' command`.

4. `core_lib.cache.cache_handler_no_cache.CacheHandlerNoCache` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_handler_no_cache.py#L6){:target="_blank"}: stores nothing, so every call runs the method. Use it to turn caching off from config.

`CacheHandlerMemcached` and `CacheHandlerRedis` store values as JSON and accept only a `dict`, `list`, `int` or `str`; anything else, such as a `float` or an entity, raises `ValueError`. A value comes back the way JSON decodes it, so dict keys become strings: `{1: 'a'}` comes back as `{'1': 'a'}`. To cache an SQLAlchemy entity, convert it with `@ResultToDict()` and put `@Cache` above it:

```python
@Cache(CACHE_KEY_USER)
@ResultToDict()
def get(self, user_id: int):
    ...
```

Decorators apply from the bottom up, so `@ResultToDict()` turns the entity into a dict first and `@Cache` stores the dict. In the opposite order, `@Cache` would try to store the entity itself.

---

### CacheRegistry

*core_lib.cache.cache_registry.CacheRegistry* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/cache/cache_registry.py#L5){:target="_blank"}

`@Cache` looks up its handler in `CoreLib.cache_registry` each time the method is called, so register the handler before the first call. `CoreLib.cache_registry` belongs to the `CoreLib` class, so there is one per process, shared by every `CoreLib` object. Registering a name twice raises `ValueError`, which is why the examples above check with `get()` first. See [Registry](registry.html).

How `get()` picks a handler:

```python
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.cache.cache_registry import CacheRegistry

cache_registry = CacheRegistry()
cache_registry.register('mem', CacheHandlerRam())

cache_registry.get('mem')    # the 'mem' handler
cache_registry.get()         # also 'mem': it is the only one

cache_registry.register('mem2', CacheHandlerRam())
cache_registry.get()         # still 'mem': with no default set, the first registered handler wins

cache_registry.register('mem3', CacheHandlerRam(), is_default=True)
cache_registry.get()         # 'mem3', the default
cache_registry.get('other')  # None: no handler by that name
```

When you register more than one handler, pass `is_default=True` to one of them, or name the handler in every `@Cache(handler_name=...)`. Otherwise a `@Cache` without `handler_name` silently uses whichever handler was registered first.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="generation.html">Previous</a></button>
    <button class="pageNext-btn"><a href="job.html">Next</a></button>
</div>
