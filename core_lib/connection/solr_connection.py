from pysolr import Solr

from core_lib.connection.connection import Connection


class SolrConnection(Connection):
    def __init__(self, solr_client: Solr):
        self._solr_client = solr_client

    def __enter__(self) -> Solr:
        return self._solr_client

    def __exit__(self, type, value, traceback):
        pass
