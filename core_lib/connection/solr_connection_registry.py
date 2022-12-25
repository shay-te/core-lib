from omegaconf import DictConfig
from pysolr import Solr

from core_lib.connection.connection_registry import ConnectionRegistry
from core_lib.connection.solr_connection import SolrConnection
from core_lib.data_layers.data.data_helpers import build_url


class SolrConnectionRegistry(ConnectionRegistry):
    def __init__(self, config: DictConfig):
        self._config = config
        self._solr_client = Solr(build_url(**config.url), always_commit=config.always_commit)

    @property
    def client(self) -> Solr:
        return self._solr_client

    def get(self, *args, **kwargs) -> SolrConnection:
        return SolrConnection(self._solr_client)
