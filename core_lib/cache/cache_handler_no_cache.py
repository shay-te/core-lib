import datetime

from core_lib.cache.cache_handler import CacheHandler
from typing import Optional


class CacheHandlerNoCache(CacheHandler):
    def __init__(self):
        """
        Initialize a cache handler with caching disabled.
        """
        self.cached_function_responses = {}

    def get(self, key):
        # Never has anything cached → always a miss.
        """
        Return a cache miss.
        
        Returns:
        	None: Always returned, indicating no cached value exists.
        """
        return None

    def set(self, key: str, value, expire: Optional[datetime.timedelta]):
        # Intentionally a no-op: this handler is the "disable caching"
        # implementation, so values are never stored.
        """
        Does not cache the provided value.
        """
        pass

    def delete(self, key: str):
        # Nothing to delete in a no-op handler.
        """
        Does not remove any cached values.
        """
        pass

    def flush_all(self):
        # Nothing to flush in a no-op handler.
        """
        Perform no operation as this handler does not store cached data.
        """
        pass
