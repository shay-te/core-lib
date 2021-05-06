from core_lib.data_layers.data.handler.data_handler_registry import DataHandlerRegistry
from core_lib.data_layers.data.handler.object_data_handler import ObjectDataHandler


class ObjectDataHandlerRegistry(DataHandlerRegistry):

    def __init__(self, obj, new_session_callback=None, close_session_callback=None):
        self._obj = obj
        self.new_session_callback = new_session_callback
        self.close_session_callback = close_session_callback

    @property
    def object(self):
        return self._obj

    def get(self, *args, **kwargs):
        obj = self._obj
        if self.new_session_callback:
            obj = self.new_session_callback(self._obj)
        return ObjectDataHandler(obj, self.close_session_callback)

