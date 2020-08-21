from core_lib.cache.cache_client import CacheClient
from core_lib.factory.default_factory import DefaultFactory


class CacheFactory(DefaultFactory):

    def __init__(self):
        DefaultFactory.__init__(self, CacheClient, error_on_no_result=True)
