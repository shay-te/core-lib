import json
from datetime import timedelta

import redis

from core_lib.cache.cache_handler import CacheHandler
from core_lib.cache.cache_helpers import validate_json_cache_value, whole_expire

ONE_MILLISECOND = timedelta(milliseconds=1)  # the smallest expire Redis keeps (`PX`)


class CacheHandlerRedis(CacheHandler):
    """Takes any key (Redis keys are binary-safe), a JSON value, and an expire to the millisecond."""

    def __init__(self, url: str):
        self.redis_client = redis.from_url(url)

    def get(self, key):
        value = self.redis_client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value, expire: timedelta):
        validate_json_cache_value(value)
        self.redis_client.set(key, json.dumps(value), px=_expire_milliseconds(expire))

    def delete(self, key: str):
        self.redis_client.delete(key)

    def flush_all(self):
        self.redis_client.flushall()


def _expire_milliseconds(expire: timedelta):
    if expire is None:
        return None  # redis-py stores the value with no expiry
    return whole_expire(expire, ONE_MILLISECOND, 'milliseconds')
