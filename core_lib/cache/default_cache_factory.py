from core_lib.cache.cache_client import CacheClient
from core_lib.factory.default_factory import DefaultFactory


class DefaultCacheFactory(DefaultFactory):

    def __init__(self):
        DefaultFactory.__init__(self, CacheClient)
