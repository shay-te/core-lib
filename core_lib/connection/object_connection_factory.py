from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.object_connection import ObjectConnection


class ObjectConnectionFactory(ConnectionFactory):
    def __init__(self, obj, new_session_callback=None, close_session_callback=None):
        self._obj = obj
        self.new_session_callback = new_session_callback
        self.close_session_callback = close_session_callback

    @property
    def object(self):
        return self._obj

    def get(self, *args, **kwargs) -> ObjectConnection:
        obj = self._obj
        if self.new_session_callback:
            obj = self.new_session_callback(self._obj)
        return ObjectConnection(obj, self.close_session_callback)
