import logging
from datetime import timedelta
from functools import wraps

from core_lib.cache.cache_client import CacheClient
from core_lib.cache.cache_key_generator import CacheKeyGenerator
from core_lib.factory.factory import Factory

logger = logging.getLogger(__name__)


class Cache(object):

    _factory = None

    # key: The key used to store the value with, when no key specified the function.__qualname__ is used
    # expire: period of time when the value is expired
    # invalidate : remove the value from the cache using the key
    # cache_client_name: what name to use to get the correct `CacheClient`
    def __init__(self,
                 key: str = None,
                 max_key_length: int = 250,
                 expire: timedelta = None,
                 invalidate: bool = False,
                 cache_client_name: str = None):
        self.key = key
        self.expire = expire
        self.invalidate = invalidate
        self.cache_client_name = cache_client_name
        self.cache_key_generator = CacheKeyGenerator(max_key_length)

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def __wrapper(*args, **kwargs):
            cache_client = self._get_cache_client()
            key = self.cache_key_generator.generate_key(self.key, func, *args, **kwargs)

            if self.invalidate:
                result = func(*args, **kwargs)
                # Invalidate the cache only after calling decorated function.
                # With the intention to make cached item available during the invalidate function rum
                cache_client.invalidate_cache(key)
                return result
            else:
                result = cache_client.from_cache(key)
                if not result:
                    result = func(*args, **kwargs)
                    cache_client.to_cache(key, result, self.expire)
                return result

        return __wrapper

    def _get_cache_client(self):
        if not Cache._factory:
            raise ValueError("factory was not set to `{}`".format(self.__class__.__name__))
        cache_client = Cache._factory.get(self.cache_client_name)

        if not cache_client:
            raise ValueError("CacheClient by name `{}` was not found in factory".format(self.cache_client_name, Cache._factory))

        if not isinstance(cache_client, CacheClient):
            raise ValueError("CacheClient by name `{}` not instance of CacheClient".format(self.cache_client_name))

        return cache_client

    @staticmethod
    def set_factory(factory: Factory):
        Cache._factory = factory
