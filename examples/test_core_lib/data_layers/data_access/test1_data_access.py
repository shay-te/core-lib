from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.sessions.db_data_session import DBDataSession


class Test1DataAccess(DataAccess):

    def __init__(self, data_sessions: list):
        DataAccess.__init__(self, data_sessions)

    def get_by_id(self, id: int):
        with self.get_session(DBDataSession.name) as session:
            return 1

    def get_by_id_2(self, id: int):
        # get the default session
        with self.get_session() as session:
            pass


