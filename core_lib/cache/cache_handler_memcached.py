import datetime
import json
import math
import time

from memcache import Client
from core_lib.cache.cache_handler import CacheHandler
from core_lib.cache.cache_helpers import validate_json_cache_value, whole_expire

NEVER_EXPIRE = 0  # memcached's "no expiry"
MAX_RELATIVE_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # memcached reads a larger expire as a Unix time
ONE_SECOND = datetime.timedelta(seconds=1)  # the smallest expire memcached keeps


class CacheHandlerMemcached(CacheHandler):
    """A store memcached refuses (over its item size limit, or the server is unreachable) answers `0` in
    python-memcached, so `set` raises. A key memcached refuses (empty, over 250 bytes, a space or a control
    character) raises python-memcached's own `MemcachedKeyError`."""

    def __init__(self, url: str):
        self.memcached_client = Client([url])

    def get(self, key):
        value = self.memcached_client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value, expire: datetime.timedelta):
        validate_json_cache_value(value)
        stored_value = json.dumps(value)
        expire_time = _expire_time(expire)
        is_stored = self.memcached_client.set(key, stored_value, time=expire_time)
        if not is_stored:
            raise RuntimeError(f'memcached did not store a value of {len(stored_value.encode())} bytes')

    def delete(self, key: str):
        self.memcached_client.delete(key)

    def flush_all(self):
        self.memcached_client.flush_all()


def _expire_time(expire: datetime.timedelta) -> int:
    if expire is None:
        return NEVER_EXPIRE
    seconds = whole_expire(expire, ONE_SECOND, 'seconds')
    if seconds > MAX_RELATIVE_EXPIRE_SECONDS:
        # memcached reads a number above 30 days as a Unix timestamp, not as seconds from now: sent as it is, 31 days
        # would be a date in January 1970, already past, and the value would be dropped without an error. So the same
        # duration goes as "now + seconds" in Unix time; `ceil` makes now a whole second, so it lasts at least `seconds`
        return math.ceil(time.time()) + seconds
    return seconds
