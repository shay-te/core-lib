from neo4j import Session

from core_lib.connection.connection import Connection


class Neo4jConnection(Connection):
    def __init__(self, neo4j_session: Session):
        self.neo4j_session = neo4j_session

    def __enter__(self) -> Session:
        return self.neo4j_session

    def __exit__(self, type, value, traceback):
        self.neo4j_session.close()
