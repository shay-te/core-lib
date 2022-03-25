import json
from datetime import timedelta

import redis

from core_lib.cache.cache_handler import CacheHandler


class CacheHandlerRedis(CacheHandler):
    def __init__(self, url: str):
        self.redis_client = redis.from_url(url)

    def get(self, key):
        value = self.redis_client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value, expire: timedelta):
        if isinstance(value, (dict, list, int, str)):
            self.redis_client.set(key, json.dumps(value), ex=expire if expire else -1)
        else:
            raise ValueError(f'result must be of type `dict` or `list`. got `{type(value)}`')

    def delete(self, key: str):
        self.redis_client.delete(key)

    def flush_all(self):
        self.redis_client.flushall()
