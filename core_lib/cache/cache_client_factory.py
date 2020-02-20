from core_lib.cache.cache_client import CacheClient


class CacheClientFactory(object):

    def __init__(self):
        self.name_to_client = {}

    # register the `CacheClient` factory by `cache_name`
    # if the `cache_name` is used, an `ValueError` is raised
    def register(self, cache_name: str, cache_client: CacheClient):
        if cache_name in self.name_to_client:
            raise ValueError("cache by name \"{}\" already registerd for type \"{}\"".format(cache_name, cache_client.__class__))

        self.name_to_client[cache_name] = cache_client

    # get the registered `CacheClient` factory by `cache_name`.
    # in case when the provided `cache_name` is None and only a Single `CacheClient` is registered,
    # the single registered client is returned.
    def get(self, cache_name):
        cache_client = self.name_to_client.get(cache_name)
        if not cache_name and len(self.name_to_client) == 1:
            cache_client = list(self.name_to_client.values())[0]
        return cache_client
