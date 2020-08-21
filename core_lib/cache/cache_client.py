from abc import ABC, abstractmethod
from datetime import timedelta


class CacheClient(ABC):

    # Fetch data from cache using the `key`, returns None when no value was found
    @abstractmethod
    def from_cache(self, key):
        pass

    # Store the `value` to cache by the `key`.
    # None `expire` will tell the storage to hold the value "forever" or after the designated period expires
    @abstractmethod
    def to_cache(self, key: str, value, expire: timedelta):
        pass

    # Remove the value from the cache using the `key`
    @abstractmethod
    def invalidate_cache(self, key: str):
        pass

