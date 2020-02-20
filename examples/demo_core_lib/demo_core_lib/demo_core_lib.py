from memcache import Client
from omegaconf import DictConfig
from core_lib.core_lib import CoreLib
from core_lib.data_layers.data.data_helpers import build_url
from core_lib.cache.cache import Cache
from core_lib.cache.cache_client_factory import CacheClientFactory
from core_lib.cache.cache_client_memcached import CacheClientMemcached

from pymongo import MongoClient
from core_lib.data_layers.data_access.sessions.object_data_session import ObjectDataSession


class DemoCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        cache_client_memcached = CacheClientMemcached(Client([build_url(**self.config.memcached)]))
        cache_factory = CacheClientFactory()
        cache_factory.register("memcached", cache_client_memcached)
        Cache.set_cache_factory(cache_factory)

        # mongo_client = MongoClient(build_url(**self.config.db))
        # mongo_db = mongo_client.demo_db
        # mongo_data_session = ObjectDataSession("mongo", mongo_db)
        #
        # self.demo = DemoService(DemoDataAccess([mongo_data_session], cache_factory))
