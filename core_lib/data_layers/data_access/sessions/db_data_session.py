from core_lib.data_layers.data.db.db_session import DBSession
from core_lib.data_layers.data_access.sessions.data_session import DataSession


class DBDataSession(DataSession):
    name = "db"

    def __init__(self, engine):
        DataSession.__init__(self, DBDataSession.name)
        self.engine = engine

    def get_session(self, params: dict):
        return DBSession(self.engine)

