import logging

from omegaconf import DictConfig
from neo4j import GraphDatabase, basic_auth

from core_lib.connection.connection_registry import ConnectionRegistry
from core_lib.connection.neo4j_connection import Neo4jConnection
from core_lib.data_layers.data.data_helpers import build_url


logger = logging.getLogger(__name__)


class Neo4jConnectionRegistry(ConnectionRegistry):
    def __init__(self, config: DictConfig):
        self._config = config
        self._neo4j_driver = GraphDatabase.driver(
            build_url(**config.url),
            auth=basic_auth(config.credentials.username, config.credentials.password),
            encrypted=False,
        )

    @property
    def driver(self) -> GraphDatabase:
        return self._neo4j_driver

    def get(self, *args, **kwargs) -> Neo4jConnection:
        return Neo4jConnection(self._neo4j_driver.session())
