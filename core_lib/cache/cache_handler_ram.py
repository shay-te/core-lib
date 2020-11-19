import datetime

from core_lib.cache.cache_handler import CacheHandler


class CacheHandlerRam(CacheHandler):

    def __init__(self):
        self.cached_function_responses = {}

    def get(self, key):
        data = self.cached_function_responses.get(key)
        if data:
            if data['expire']:
                set_time_diff = datetime.datetime.utcnow() - data['set_time']
                if set_time_diff < data['expire']:
                    return data['data']
                else:
                    del self.cached_function_responses[key]
            else:
                return data['data']
        return None

    def set(self, key: str, value, expire: datetime.timedelta):
        self.cached_function_responses[key] = {'data': value, 'set_time': datetime.datetime.utcnow(), 'expire': expire}

    def delete(self, key: str):
        if key in self.cached_function_responses:
            del self.cached_function_responses[key]
