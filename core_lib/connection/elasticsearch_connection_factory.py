import warnings

from omegaconf import DictConfig

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.elasticsearch_connection import ElasticsearchConnection
from core_lib.data_layers.data.data_helpers import build_url
from elasticsearch import Elasticsearch


class ElasticsearchConnectionFactory(ConnectionFactory):

    def __init__(self, config: DictConfig):
        self._elastic_search_client = Elasticsearch(build_url(**config.url))

    @property
    def client(self) -> Elasticsearch:
        return self._elastic_search_client

    def get(self, *args, **kwargs):
        return ElasticsearchConnection(self._elastic_search_client)


def __getattr__(name):
    # Deprecated since 0.3.0, to be removed in 1.0.0: the old spelling of the class name. The product is
    # "Elasticsearch". tests/test_deprecated_aliases.py fails at 1.0.0 if this is still here.
    if name == 'ElasticSearchConnectionFactory':
        warnings.warn(
            '`ElasticSearchConnectionFactory` is deprecated since 0.3.0 and will be removed in 1.0.0, use `ElasticsearchConnectionFactory` instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return ElasticsearchConnectionFactory
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
