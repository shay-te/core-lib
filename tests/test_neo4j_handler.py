import unittest

import hydra
from neo4j import Neo4jDriver
from pysolr import Solr

from core_lib.data_layers.data.handler.neo4j_data_handler import Neo4jDataHandler
from core_lib.data_layers.data.handler.neo4j_data_handler_registry import Neo4jDataHandlerRegistry
from core_lib.helpers.config_instances import instantiate_config


class TestNeo4jHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        hydra.core.global_hydra.GlobalHydra.instance().clear()
        hydra.initialize(config_path='./test_data/test_config')

    def test_instantiate(self):
        config_file = 'test_neo4j.yaml'
        config = hydra.compose(config_file)
        neo4j = instantiate_config(config.core_lib.neo4j)
        self.assertIsInstance(neo4j, Neo4jDataHandlerRegistry)
        self.assertIsInstance(neo4j.driver, Neo4jDriver)
        self.assertIsInstance(neo4j.get(), Neo4jDataHandler)

