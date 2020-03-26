from core_lib.data_layers.data_access.sessions.object_data_session import ObjectDataSession
from core_lib.factory.factory import Factory


class ObjectDataSessionFactory(Factory):

    def __init__(self, obj):
        self.obj = obj

    def get(self, *args, **kwargs):
        return ObjectDataSession(self.obj)

