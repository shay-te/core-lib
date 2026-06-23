import json
from datetime import timedelta

import redis

from core_lib.cache.cache_handler import CacheHandler
from typing import Optional


class CacheHandlerRedis(CacheHandler):
    def __init__(self, url: str):
        """
        Initialize the Redis cache handler with a connection URL.
        
        Parameters:
        	url (str): Redis connection URL
        """
        self.redis_client = redis.from_url(url)

    def get(self, key):
        """
        Retrieve a cached value from Redis.
        
        Parameters:
            key (str): The cache key to retrieve.
        
        Returns:
            The cached value if the key exists, `None` otherwise.
        """
        value = self.redis_client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value, expire: Optional[timedelta]):
        # Accept any JSON-serializable primitive plus dict / list. Float was
        # previously excluded for no clear reason — json.dumps handles it.
        """
        Store a value in the Redis cache with optional expiration.
        
        Parameters:
            value: A JSON-serializable value (dict, list, int, float, or str)
            expire (Optional[timedelta]): Duration until the cached value expires. If None, the value persists without expiration.
        
        Raises:
            ValueError: If value is not of an allowed JSON-serializable type.
        """
        if not isinstance(value, (dict, list, int, float, str)):
            raise ValueError(
                f'result must be a JSON-serializable type '
                f'(dict, list, int, float, str). got `{type(value)}`'
            )
        serialized = json.dumps(value)
        # Pass `ex=` only when there's a real expiry. The previous default
        # `ex=-1` triggered "ERR invalid expire time" on the Redis server
        # for any cache set without an explicit timedelta.
        if expire:
            self.redis_client.set(key, serialized, ex=expire)
        else:
            self.redis_client.set(key, serialized)

    def delete(self, key: str):
        """
        Removes a key from the cache.
        """
        self.redis_client.delete(key)

    def flush_all(self):
        """
        Remove all keys from the Redis database.
        """
        self.redis_client.flushall()
