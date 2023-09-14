from core_lib.connection.connection import Connection
from elasticsearch import Elasticsearch


class ElasticSearchConnection(Connection):
    def __init__(self, elastic_search_client: Elasticsearch):
        self.elastic_search_client = elastic_search_client

    def __enter__(self) -> Elasticsearch:
        return self.elastic_search_client

    def __exit__(self, exec_type, exec_value, traceback):
        """
        Skipped because this a exit function and returns nothing
        """
        pass
