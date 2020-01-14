import json
import logging
from datetime import timedelta, datetime
from memcache import Client
from core_lib.cache.cache_base import CacheBase

logger = logging.getLogger('CacheMemcached')


class CacheMemcached(CacheBase):

    memcached = None

    def from_cache(self, key):
        return CacheMemcached.__client().get(key, self.expire)

    def to_cache(self, key: str, value, time: timedelta):
        if isinstance(value, dict):
            CacheMemcached.__client().set(key, json.dumps(value), time=self.__delta_to_seconds(self.expire))
        else:
            raise ValueError('result must be of type "dict"')

    def invalidate_cache(self, key: str):
        CacheMemcached.__client().delete(key)

    def __delta_to_seconds(self, expire: timedelta):
        return expire.total_seconds if expire and isinstance(expire, datetime.timedelta) else None

    @staticmethod
    def __client():
        if not CacheMemcached.memcached:
            raise ValueError('CacheMemcached.client was never set. please use "CacheMemcached.set_client(client...)"')
        return CacheMemcached.memcached

    @staticmethod
    def set_client(client: Client):
        CacheMemcached.memcached = client