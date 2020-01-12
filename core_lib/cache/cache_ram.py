import datetime
from core_lib.cache.cache_base import CacheBase
from datetime import timedelta


class CacheRam(CacheBase):
    cached_function_responses = {}

    def __init__(self, *args, **kwargs):
        CacheBase.__init__(self, *args, **kwargs)

    def from_cache(self, key):
        data = CacheRam.cached_function_responses.get(key)
        if data:
            if self.expire:
                if datetime.datetime.now() - data['set_time'] < self.expire:
                    return data['data']
                else:
                    del CacheRam.cached_function_responses[key]
            else:
                return data['data']
        return None

    def to_cache(self, key: str, value, time: timedelta):
        CacheRam.cached_function_responses[key] = {'data': value, 'set_time': datetime.datetime.now()}

    def invalidate_cache(self, key: str):
        if key in CacheRam.cached_function_responses:
            del CacheRam.cached_function_responses[key]
