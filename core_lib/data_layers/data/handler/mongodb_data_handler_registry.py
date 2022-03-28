from omegaconf import DictConfig
from pymongo import MongoClient

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.data_handler_registry import DataHandlerRegistry


class MongoDBDataHandlerRegistry(DataHandlerRegistry):
    def __init__(self, config: DictConfig):
        self._mongo_client = MongoClient(build_url(**config.url))

    @property
    def client(self) -> MongoClient:
        return self._mongo_client
