from omegaconf import DictConfig
import pysolr
from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.data_handler_factory import DataHandlerFactory
from core_lib.data_layers.data.handler.solr_data_handler import SolrDataHandler


class SolrDataHandlerFactory(DataHandlerFactory):

    def __init__(self, config: DictConfig):
        self._config = config
        solr_address = build_url(**config.url)
        self._solr_client = pysolr.Solr(solr_address, always_commit=config.always_commit)

    def get(self, *args, **kwargs):
        return SolrDataHandler(self._solr_client)
