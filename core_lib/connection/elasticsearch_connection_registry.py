from omegaconf import DictConfig
from core_lib.connection.connection_registry import ConnectionRegistry
from core_lib.connection.elasticsearch_connection import ElasticSearchConnection
from core_lib.data_layers.data.data_helpers import build_url
from elasticsearch import Elasticsearch


class ElasticSearchConnectionRegistry(ConnectionRegistry):

    def __init__(self, config: DictConfig):
        self._elastic_search_client = Elasticsearch(build_url(**config.url))

    @property
    def client(self) -> Elasticsearch:
        return self._elastic_search_client

    def get(self, *args, **kwargs):
        return ElasticSearchConnection(self._elastic_search_client)
