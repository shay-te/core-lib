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
        # Accept any JSON-serializable primitive plus dict / list. Float was
        # previously excluded for no clear reason.
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
        self.memcached_client.delete(key)

    def flush_all(self):
        self.memcached_client.flush_all()
