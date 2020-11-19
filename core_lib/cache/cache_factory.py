from core_lib.cache.cache_handler import CacheHandler
from core_lib.factory.default_factory import DefaultRegistry


class CacheRegistry(DefaultRegistry):

    def __init__(self):
        DefaultRegistry.__init__(self, CacheHandler, error_on_no_result=True)
