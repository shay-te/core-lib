from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.sessions.db_data_session_factory import DBDataSessionFactory


class Test2DataAccess(DataAccess):

    def __init__(self, data_sessions: list):
        DataAccess.__init__(self, data_sessions)

    def get_by_id(self, id: int):
        with self.get_session(DBDataSessionFactory.name) as session:
            pass

    def get_by_id_2(self, id: int):
        # get the default session
        with self.get_session() as session:
            pass


