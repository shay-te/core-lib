import logging

from omegaconf import DictConfig
from neo4j import GraphDatabase, basic_auth

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.connection.data_handler_registry import ConnectionRegistry
from core_lib.connection.neo4j_data_handler import Neo4JConnection


logger = logging.getLogger(__name__)


class Neo4JConnectionRegistry(ConnectionRegistry):
    def __init__(self, config: DictConfig):
        self._config = config
        logger.info(f'Neo4jDataHandlerRegistry: {build_url(**config.url)}, config: {config}')
        self._neo4j_driver = GraphDatabase.driver(
            build_url(**config.url),
            auth=basic_auth(config.credentials.username, config.credentials.password),
            encrypted=False,
        )

    @property
    def driver(self) -> GraphDatabase:
        return self._neo4j_driver

    def get(self, *args, **kwargs) -> Neo4JConnection:
        return Neo4JConnection(self._neo4j_driver.session())
