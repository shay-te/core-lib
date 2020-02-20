from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.sessions.data_session_factory import DataSessionFactory
from core_lib.data_layers.data_access.sessions.db_data_session_factory import DBDataSessionFactory


class Test1DataAccess(DataAccess):

    def __init__(self, data_session_factory: DataSessionFactory):
        DataAccess.__init__(self, data_session_factory)

    def get_by_id(self, id: int):
        with self.get_session(DBDataSessionFactory.name) as session:
            return 1

    def get_by_id_2(self, id: int):
        # get the default session
        with self.get_session() as session:
            pass


    def create_test_info(self, data):
        TestInfo

