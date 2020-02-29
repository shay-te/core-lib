from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.sessions.data_session_factory import DataSessionFactory
from core_lib.data_layers.data_access.sessions.object_data_session_factory import ObjectDataSessionFactory


class Test2DataAccess(DataAccess):

    def get_value(self):
        return 2