from memcache import Client
from omegaconf import OmegaConf
from pymongo import MongoClient

from core_lib.cache.cache_memcashed import CacheMemcached
from core_lib.core_lib import CoreLib
from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data_access.sessions.object_data_session import ObjectDataSession
from examples.demo_core_lib.data_layers.data_access.demo_data_access import DemoDataAccess
from examples.demo_core_lib.data_layers.service.demo_service import DemoService


class DemoCoreLib(CoreLib):

    def __init__(self, conf: OmegaConf):
        self.config = conf

        CacheMemcached.set_client(Client([build_url(**self.config.memcached)]))

        mongo_client = MongoClient(build_url(**self.config.db))
        mongo_db = mongo_client.demo_db
        mongo_data_session = ObjectDataSession("mongo", mongo_db)

        self.demo = DemoService(DemoDataAccess([mongo_data_session]))
