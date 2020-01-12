import datetime
import json
from datetime import timedelta
from memcache import Client


class MemcachedClient(object):

    __instance = None

    def __init__(self, host: str, port: int):
        self.memcached_client = Client(['{}:{}'.format(host, port)])

    @staticmethod
    def init(host='localhost', port=11211):
        if MemcachedClient.__instance is None:
            MemcachedClient.__instance = MemcachedClient(host, port)

    @staticmethod
    def memcached():
        if MemcachedClient.__instance is None: raise NameError('MemcachedClient not initialized')
        return MemcachedClient.__instance.memcached_client

    @staticmethod
    def merge_update_dict(key, dict_data, expire: timedelta = None):
        if MemcachedClient.__instance is None: raise NameError('MemcachedClient not initialized')

        result = MemcachedClient.memcached().get(key)
        if result:
            json_result = json.dumps(result)
            for data_key, value in dict_data.items():
                if data_key in json_result:
                    json_result[data_key] = value

            MemcachedClient.memcached().set(key, json.loads(json_result), time=MemcachedClient.__delta_to_seconds(timedelta))

    @staticmethod
    def __delta_to_seconds(expire: timedelta):
        return expire.total_seconds() if expire and isinstance(expire, datetime.timedelta) else None



