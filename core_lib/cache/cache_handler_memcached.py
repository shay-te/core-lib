import datetime
import json

from memcache import Client
from core_lib.cache.cache_handler import CacheHandler
from typing import Optional


class CacheHandlerMemcached(CacheHandler):
    def __init__(self, url: str):
        """
        Initialize the cache handler with a Memcached connection.
        
        Parameters:
        	url (str): URL of the Memcached server
        """
        self.memcached_client = Client([url])

    def get(self, key):
        """
        Retrieve a value from Memcached and deserialize it from JSON.
        
        Returns:
            The deserialized object, or None if the key is not found.
        """
        value = self.memcached_client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value, expire: Optional[datetime.timedelta]):
        # Accept any JSON-serializable primitive plus dict / list. Float was
        # previously excluded for no clear reason.
        """
        Store a JSON-serializable value in Memcached with optional expiration.
        
        Parameters:
            key (str): The cache key identifying the value.
            value: A JSON-serializable type: dict, list, int, float, or str.
            expire (Optional[datetime.timedelta]): Time until the cached value expires.
                If None, the value does not expire.
        
        Raises:
            ValueError: If value is not a JSON-serializable type.
        """
        if not isinstance(value, (dict, list, int, float, str)):
            raise ValueError(
                f'result must be a JSON-serializable type '
                f'(dict, list, int, float, str). got `{type(value)}`'
            )
        # memcached treats time=0 as "never expires", which is what we want
        # when no explicit expiry was provided.
        self.memcached_client.set(
            key,
            json.dumps(value),
            time=expire.total_seconds() if expire else 0,
        )

    def delete(self, key: str):
        """
        Delete the cached entry for the specified key.
        
        Parameters:
        	key (str): The cache key to delete
        """
        self.memcached_client.delete(key)

    def flush_all(self):
        """
        Clears all entries from the Memcached cache.
        """
        self.memcached_client.flush_all()
