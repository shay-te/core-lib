import datetime

from core_lib.cache.cache_handler import CacheHandler


class CacheHandlerRam(CacheHandler):

    def __init__(self):
        self.cached_function_responses = {}

    def from_cache(self, key):
        data = self.cached_function_responses.get(key)
        if data:
            if data['expire']:
                if datetime.datetime.now() - data['set_time'] < data['expire']:
                    return data['data']
                else:
                    del self.cached_function_responses[key]
            else:
                return data['data']
        return None

    def to_cache(self, key: str, value, expire: datetime.timedelta):
        self.cached_function_responses[key] = {'data': value, 'set_time': datetime.datetime.now(), 'expire': expire}

    def invalidate_cache(self, key: str):
        if key in self.cached_function_responses:
            del self.cached_function_responses[key]
