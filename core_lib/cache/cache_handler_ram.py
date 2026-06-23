import datetime

from core_lib.cache.cache_handler import CacheHandler
from typing import Optional


class CacheHandlerRam(CacheHandler):
    def __init__(self, *args, **kwargs):
        """
        Initialize an in-memory cache for storing function responses.
        """
        self.cached_function_responses = {}

    def get(self, key):
        """
        Retrieves cached data for a key, removing expired entries.
        
        Returns:
            The cached value if the key exists and has not expired; `None` otherwise.
        """
        data = self.cached_function_responses.get(key)
        if data:
            if data['expire']:
                set_time_diff = datetime.datetime.utcnow() - data['set_time']
                if set_time_diff < data['expire']:
                    return data['data']
                else:
                    del self.cached_function_responses[key]
            else:
                return data['data']
        return None

    def set(self, key: str, value, expire: Optional[datetime.timedelta]):
        """
        Store a value in the cache with an optional expiration duration.
        
        Parameters:
        	expire: Duration after which the cached value expires. If None, the value does not expire.
        """
        self.cached_function_responses[key] = {'data': value, 'set_time': datetime.datetime.utcnow(), 'expire': expire}

    def delete(self, key: str):
        """
        Remove a cached entry by key.
        """
        if key in self.cached_function_responses:
            del self.cached_function_responses[key]

    def flush_all(self):
        """
        Clear all cached entries.
        """
        self.cached_function_responses = {}
