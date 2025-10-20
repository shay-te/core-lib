from omegaconf import DictConfig
import pymongo

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.mongodb_connection import MongoDBConnection
from core_lib.data_layers.data.data_helpers import build_url


class MongoDBConnectionFactory(ConnectionFactory):

    def __init__(self, config: DictConfig):
        self._mongo_client = pymongo.MongoClient(build_url(**config.url))

    @property
    def client(self) -> pymongo.MongoClient:
        return self._mongo_client

    def get(self, *args, **kwargs):
        return MongoDBConnection(self._mongo_client)
