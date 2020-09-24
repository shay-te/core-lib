from hydra.utils import instantiate
from memcache import Client

from core_lib.cache.cache_handler import CacheHandler
from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached
from core_lib.cache.cache_handler_no_cache import CacheHandlerNoCache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.data_layers.data.data_helpers import build_url


def connect_cache(config, name: str):
    cache_config = config.core_lib.cache.get(name)
    if not cache_config:
        raise ValueError('Cache by name `{}` not found in config'.format(cache_config))
    handler = cache_config['handler']
    if handler:
        try:
            processor = instantiate(handler)
            if not isinstance(processor, CacheHandler):
                raise ValueError("cache must be a baseclass of 'CacheHandler'. Got: {} ".format(handler.__class__.__name__))
        except Exception as e:
            raise ValueError('unable to instantiate cache') from e


def connect_no_cache():
    return CacheHandlerNoCache()


def connect_cache_ram():
    return CacheHandlerRam()


def connect_cache_memcached(config):
    return CacheHandlerMemcached(Client([build_url(**config.url)]))
