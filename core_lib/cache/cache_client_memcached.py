import datetime
import json

from memcache import Client
from core_lib.cache.cache_client import CacheClient


class CacheClientMemcached(CacheClient):

    def __init__(self, memcached_client: Client):
        self.memcached_client = memcached_client

    def from_cache(self, key):
        value = self.memcached_client.get(key)
        return json.loads(value) if value else None

    def to_cache(self, key: str, value, expire: datetime.timedelta):
        if isinstance(value, (dict, list)):
            self.memcached_client.set(key, json.dumps(value), time=expire.total_seconds() if expire else 0)
        else:
            raise ValueError('result must be of type `dict` or `list`')

    def invalidate_cache(self, key: str):
        self.memcached_client.delete(key)
