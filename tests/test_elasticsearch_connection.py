import unittest
import hydra
from elasticsearch import Elasticsearch

from core_lib.connection.elasticsearch_connection_registry import ElasticSearchConnectionRegistry
from core_lib.helpers.config_instances import instantiate_config

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='./test_data/test_config')
configfile = "test_elasticsearch.yaml"
config = hydra.compose(configfile)


class TestElasticsearchConnection(unittest.TestCase):
    def test_connection(self):
        connection = instantiate_config(config.core_lib.elasticsearch)
        self.assertIsInstance(connection, ElasticSearchConnectionRegistry)
        client = connection.client
        self.assertIsInstance(client, Elasticsearch)
