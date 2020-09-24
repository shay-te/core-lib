from core_lib.cache.cache_handler import CacheHandler
from core_lib.factory.default_factory import DefaultFactory


class CacheFactory(DefaultFactory):

    def __init__(self):
        DefaultFactory.__init__(self, CacheHandler, error_on_no_result=True)
