from core_lib.cache.cache_handler import CacheHandler
from core_lib.registry.default_registry import DefaultRegistry


class CacheRegistry(DefaultRegistry):

    def __init__(self):
        DefaultRegistry.__init__(self, CacheHandler)
