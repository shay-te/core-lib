from omegaconf import DictConfig
import pymongo
from core_lib.connection.connection_registry import ConnectionRegistry
from core_lib.connection.mongodb_connection import MongoDBConnection
from core_lib.data_layers.data.data_helpers import build_url


class MongoDBConnectionRegistry(ConnectionRegistry):

    def __init__(self, config: DictConfig):
        self._mongo_client = pymongo.MongoClient(build_url(**config.url))

    @property
    def client(self) -> pymongo.MongoClient:
        return self._mongo_client

    def get(self, *args, **kwargs):
        return MongoDBConnection(self._mongo_client)
