from omegaconf import DictConfig
from pysolr import Solr

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.data_handler_factory import DataHandlerRegistry
from core_lib.data_layers.data.handler.solr_data_handler import SolrDataHandler


class SolrDataHandlerFactory(DataHandlerRegistry):

    def __init__(self, config: DictConfig):
        self._config = config
        solr_address = build_url(**config.url)
        self._solr_client = Solr(solr_address, always_commit=config.always_commit)

    def get(self, *args, **kwargs) -> SolrDataHandler:
        return SolrDataHandler(self._solr_client)
