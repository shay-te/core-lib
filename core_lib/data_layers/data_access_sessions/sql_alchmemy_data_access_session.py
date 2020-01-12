from core_lib.data_layers.data.db.db_session import DBSession
from core_lib.data_layers.data_access_sessions.data_access_session import DataAccessSession


class SqlAlchmemyDataAccessSession(DataAccessSession):

    def __init__(self, engine):
        DataAccessSession.__init__('sql_alchemy')
        self.engine = engine

    def get_session(self, params: dict):
        # possible to get connection by data
        return DBSession(self.engine)

