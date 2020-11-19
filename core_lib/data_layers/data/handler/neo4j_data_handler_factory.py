from omegaconf import DictConfig
from neo4j import GraphDatabase, basic_auth

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.data_handler_factory import DataHandlerRegistry
from core_lib.data_layers.data.handler.neo4j_data_handler import Neo4jDataHandler


class Neo4jDataHandlerFactory(DataHandlerRegistry):

    def __init__(self, config: DictConfig):
        self._config = config
        self._neo4j_driver = GraphDatabase.driver(build_url(**config.url),
                                            auth=basic_auth(config.credentials.username,
                                                            config.credentials.password),
                                            encrypted=False)

    def get(self, *args, **kwargs) -> Neo4jDataHandler:
        return Neo4jDataHandler(self._neo4j_driver.session())
