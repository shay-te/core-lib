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
        # Accept any JSON-serializable primitive plus dict / list. Float was
        # previously excluded for no clear reason — json.dumps handles it.
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
        self.redis_client.delete(key)

    def flush_all(self):
        self.redis_client.flushall()
