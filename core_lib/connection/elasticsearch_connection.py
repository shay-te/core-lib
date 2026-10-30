import warnings

from core_lib.connection.connection import Connection
from elasticsearch import Elasticsearch


class ElasticsearchConnection(Connection):
    def __init__(self, elastic_search_client: Elasticsearch):
        self.elastic_search_client = elastic_search_client

    def __enter__(self) -> Elasticsearch:
        return self.elastic_search_client

    def __exit__(self, exec_type, exec_value, traceback):
        """
        Skipped because this a exit function and returns nothing
        """
        pass


def __getattr__(name):
    # Deprecated since 0.3.0, to be removed in 1.0.0: the old spelling of the class name. The product is
    # "Elasticsearch". tests/test_deprecated_aliases.py fails at 1.0.0 if this is still here.
    if name == 'ElasticSearchConnection':
        warnings.warn(
            '`ElasticSearchConnection` is deprecated since 0.3.0 and will be removed in 1.0.0, use `ElasticsearchConnection` instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return ElasticsearchConnection
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
