import inspect
from datetime import timedelta
from core_lib.cache.cache_client_factory import CacheClientFactory


class Cache(object):

    _cache_factory = None

    # key: The key used to store the value with, when no key specified the function.__qualname__ is used
    # expire: period of time when the value is expired
    # invalidate : remove the value from the cache using the key
    # cache_client_name: what name to use to get the correct `CacheClient`
    def __init__(self, key: str = None, expire: timedelta = None, invalidate: bool = False, cache_client_name: str = None):
        self.key = key
        self.expire = expire
        self.invalidate = invalidate
        self.cache_client_name = cache_client_name

    def __call__(self, func, *args, **kwargs):

        def __wrapper(*args, **kwargs):
            cache_client = self._get_cache_client()
            key = self.__generate_key(func, *args, **kwargs)

            if self.invalidate:
                cache_client.invalidate_cache(key)
                return func(*args, **kwargs)
            else:
                result = cache_client.from_cache(key)
                if not result:
                    result = func(*args, **kwargs)
                    cache_client.to_cache(key, result, self.expire)
                return result

        return __wrapper

    def __generate_key(self, func, *args, **kwargs):
        if self.key:
            format_params = {}
            args_len = len(args)
            for index, arg in enumerate(inspect.getfullargspec(func).args):
                if arg is not 'self':
                    if index < args_len:
                        format_params[arg] = args[index]
                    else: 
                        format_params[arg] = kwargs[arg] if arg in kwargs else '_'  # Handle optional parameters
            return self.key.format(**format_params)
        else:
            return func.__qualname__

    def _get_cache_client(self):
        if not Cache._cache_factory:
            raise ValueError("CacheClientFactory was not set to \"{}\"".format(self.__class__.__name__))
        cache_client = Cache._cache_factory.get(self.cache_client_name)
        if not cache_client:
            raise ValueError("CacheClient by name \"{}\". is not registered under factory \"{}\"".format(self.cache_client_name, Cache._cache_factory))
        return cache_client

    @staticmethod
    def set_cache_factory(cache_factory: CacheClientFactory):
        Cache._cache_factory = cache_factory
