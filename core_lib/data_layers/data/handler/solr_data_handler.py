from pysolr import Solr

from core_lib.data_layers.data.handler.data_handler import DataHandler


class SolrDataHandler(DataHandler):

    def __init__(self, solr_client):
        self._solr_client = solr_client

    def __enter__(self) -> Solr:
        return self._solr_client

    def __exit__(self, type, value, traceback):
        pass
