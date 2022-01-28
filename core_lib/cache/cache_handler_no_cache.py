import datetime

from core_lib.cache.cache_handler import CacheHandler


class CacheHandlerNoCache(CacheHandler):

    def __init__(self):
        self.cached_function_responses = {}

    def get(self, key):
        return None

    def set(self, key: str, value, expire: datetime.timedelta):
        pass

    def delete(self, key: str):
        pass
