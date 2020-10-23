from neo4j import Session

from core_lib.data_layers.data.handler.data_handler import DataHandler


class Neo4jDataHandler(DataHandler):

    def __init__(self, neo4j_session):
        self.neo4j_session = neo4j_session

    def __enter__(self) -> Session:
        return self.neo4j_session

    def __exit__(self, type, value, traceback):
        self.neo4j_session.close()
