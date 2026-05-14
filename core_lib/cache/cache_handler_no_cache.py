import datetime

from core_lib.cache.cache_handler import CacheHandler
from typing import Optional


class CacheHandlerNoCache(CacheHandler):
    def __init__(self):
        self.cached_function_responses = {}

    def get(self, key):
        # Never has anything cached → always a miss.
        return None

    def set(self, key: str, value, expire: Optional[datetime.timedelta]):
        # Intentionally a no-op: this handler is the "disable caching"
        # implementation, so values are never stored.
        pass

    def delete(self, key: str):
        # Nothing to delete in a no-op handler.
        pass

    def flush_all(self):
        # Nothing to flush in a no-op handler.
        pass
