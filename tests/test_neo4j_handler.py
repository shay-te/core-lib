import unittest

import hydra
from neo4j import Neo4jDriver

from core_lib.connection.neo4j_connection import Neo4jConnection
from core_lib.connection.neo4j_connection_registry import Neo4jConnectionRegistry
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
        self.assertIsInstance(neo4j, Neo4jConnectionRegistry)
        self.assertIsInstance(neo4j.driver, Neo4jDriver)
        self.assertIsInstance(neo4j.get(), Neo4jConnection)

