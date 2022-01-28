from datetime import timedelta

from core_lib.cache.cache_decorator import Cache
from core_lib.data_layers.data_access.data_access import DataAccess


class SlowLargeDataDataAccess(DataAccess):
    def __init__(self):
        self.data = {"data": "i weight allot"}

    @Cache(key='large_data_cache_key', expire=timedelta(seconds=5))
    def get_data(self):
        return self.data

    @Cache(key='large_data_cache_key', invalidate=True)
    def set_data(self, data):
        self.data = data

    def set_data_local(self, data):
        self.data = data
