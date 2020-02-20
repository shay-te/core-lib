from core_lib.data_layers.data_access.sessions.data_session_factory import DataSessionFactory
from core_lib.data_layers.data_access.sessions.object_data_session import ObjectDataSession


class ObjectDataSessionFactory(DataSessionFactory):

    def __init__(self, obj):
        self.obj = obj

    def get_session(self, name: str = None, params: dict = None):
        if name and name != "db":
            raise ValueError("name not registered.")
        return ObjectDataSession(self.obj)

