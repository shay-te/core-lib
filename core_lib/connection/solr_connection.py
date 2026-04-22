from core_lib.connection.connection import Connection

try:
    from pysolr import Solr
except ImportError:
    raise ImportError("pip install pysolr to use Solr connections")


class SolrConnection(Connection):
    def __init__(self, solr_client: Solr):
        self._solr_client = solr_client

    def __enter__(self) -> Solr:
        return self._solr_client

    def __exit__(self, type, value, traceback):
        pass
