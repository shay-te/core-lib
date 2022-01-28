from dataclasses import dataclass

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING

import core_lib


@dataclass
class RamCacheConfig:
    _target_: str = core_lib.cache.cache_handler_ram.CacheHandlerRam


@dataclass
class NoCacheConfig:
    _target_: str = core_lib.cache.cache_handler_no_cache.CacheHandlerNoCache


@dataclass
class MemcachedCacheConfig:
    _target_: str = core_lib.cache.cache_handler_memcached.CacheHandlerMemcached
    host: str = MISSING
    port: int = MISSING


cs = ConfigStore.instance()
cs.store(name="ram_cache", node=RamCacheConfig)
cs.store(name="no_cache", node=NoCacheConfig)
cs.store(name="memcached_cache", node=MemcachedCacheConfig)

