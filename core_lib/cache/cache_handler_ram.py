import datetime

from core_lib.cache.cache_handler import CacheHandler
from core_lib.cache.cache_helpers import whole_expire

ONE_MICROSECOND = datetime.timedelta(microseconds=1)  # timedelta's own precision: RAM keeps any expire


class CacheHandlerRam(CacheHandler):
    def __init__(self, *args, **kwargs):
        self.cached_function_responses = {}

    def get(self, key):
        data = self.cached_function_responses.get(key)
        if data:
            if data['expire']:
                set_time_diff = datetime.datetime.utcnow() - data['set_time']
                if set_time_diff < data['expire']:
                    return data['data']
                else:
                    self.cached_function_responses.pop(key, None)  # another thread may have removed it already
            else:
                return data['data']
        return None

    def set(self, key: str, value, expire: datetime.timedelta):
        if expire is not None:
            whole_expire(expire, ONE_MICROSECOND, 'microseconds')  # refuses 0 or less; any other time is kept
        self.cached_function_responses[key] = {'data': value, 'set_time': datetime.datetime.utcnow(), 'expire': expire}

    def delete(self, key: str):
        self.cached_function_responses.pop(key, None)

    def flush_all(self):
        self.cached_function_responses = {}
