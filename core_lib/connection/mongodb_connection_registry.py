from omegaconf import DictConfig
from pymongo import MongoClient

from core_lib.connection.connection_registry import ConnectionRegistry
from core_lib.connection.mongodb_connection import MongoDBConnection
from core_lib.data_layers.data.data_helpers import build_url


class MongoDBConnectionRegistry(ConnectionRegistry):

    def __init__(self, config: DictConfig):
        self._mongo_client = MongoClient(build_url(**config.url))

    @property
    def client(self) -> MongoClient:
        return self._mongo_client

    def get(self, *args, **kwargs):
        return self._mongo_client
