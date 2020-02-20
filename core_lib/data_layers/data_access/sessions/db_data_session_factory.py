from core_lib.data_layers.data_access.sessions.db_data_session import DBDataSession
from core_lib.data_layers.data_access.sessions.data_session import DataSession
from core_lib.data_layers.data_access.sessions.data_session_factory import DataSessionFactory


class DBDataSessionFactory(DataSessionFactory):
    name = "db"

    def __init__(self, engine):
        self.engine = engine

    def get_session(self, name: str = None, params: dict = None):
        if name and name != "db":
            raise ValueError("name not registered.")
        return DBDataSession(self.engine)

