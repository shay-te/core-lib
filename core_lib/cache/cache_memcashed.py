import json
from datetime import timedelta

from core_lib.cache.cache_base import CacheBase
from core_lib.data_layers.data.memcached.memcached_client import MemcachedClient


class CacheMemcached(CacheBase):

    def __init__(self, *args, **kwargs):
        CacheBase.__init__(self, *args, **kwargs)

    def from_cache(self, key):
        return MemcachedClient.memcached().get(key, self.expire)

    def to_cache(self, key: str, value, time: timedelta):
        if isinstance(value, dict):
            MemcachedClient.memcached().set(key, json.dumps(value), time=MemcachedClient.__delta_to_seconds(self.expire))
        else:
            raise ValueError('result must be of type "dict"')

    def invalidate_cache(self, key: str):
        MemcachedClient.memcached().delete(key)
