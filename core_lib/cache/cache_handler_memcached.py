import datetime
import json

from memcache import Client
from core_lib.cache.cache_handler import CacheHandler


class CacheHandlerMemcached(CacheHandler):

    def __init__(self, memcached_client: Client):
        assert isinstance(memcached_client, Client)
        self.memcached_client = memcached_client

    def get(self, key):
        value = self.memcached_client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value, expire: datetime.timedelta):
        if isinstance(value, (dict, list, int, str)):
            self.memcached_client.set(key, json.dumps(value), time=expire.total_seconds() if expire else 0)
        else:
            raise ValueError('result must be of type `dict` or `list`')

    def delete(self, key: str):
        self.memcached_client.delete(key)
