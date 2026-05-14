import datetime

from core_lib.cache.cache_handler import CacheHandler
from typing import Optional


class CacheHandlerNoCache(CacheHandler):
    def __init__(self):
        self.cached_function_responses = {}

    def get(self, key):
        return None

    def set(self, key: str, value, expire: Optional[datetime.timedelta]):
        pass

    def delete(self, key: str):
        pass

    def flush_all(self):
        pass
