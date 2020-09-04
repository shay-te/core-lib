from core_lib.data_layers.data.session.data_session_factory import DataSessionFactory
from core_lib.data_layers.data.session.object_data_session import ObjectDataSession


class ObjectDataSessionFactory(DataSessionFactory):

    def __init__(self, obj, new_session_callback=None, close_session_callback=None):
        self.obj = obj
        self.new_session_callback = new_session_callback
        self.close_session_callback = close_session_callback

    def get(self, *args, **kwargs):
        obj = self.obj
        if self.new_session_callback:
            obj = self.new_session_callback(self.obj)
        return ObjectDataSession(obj, self.close_session_callback)

