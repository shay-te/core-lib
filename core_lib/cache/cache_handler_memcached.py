import datetime
import json

from memcache import Client
from core_lib.cache.cache_handler import CacheHandler


class CacheHandlerMemcached(CacheHandler):
    def __init__(self, url: str):
        self.memcached_client = Client([url])

    def get(self, key):
        value = self.memcached_client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value, expire: datetime.timedelta):
        if isinstance(value, (dict, list, int, str)):
            self.memcached_client.set(key, json.dumps(value), time=expire.total_seconds() if expire else 0)
        else:
            raise ValueError(f'result must be of type `dict` or `list`. got `{type(value)}`')

    def delete(self, key: str):
        self.memcached_client.delete(key)

    def flush_all(self):
        self.memcached_client.flush_all()
