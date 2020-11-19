from core_lib.data_layers.data.handler.data_handler_factory import DataHandlerRegistry
from core_lib.data_layers.data.handler.object_data_handler import ObjectDataHandler


class ObjectDataHandlerFactory(DataHandlerRegistry):

    def __init__(self, obj, new_session_callback=None, close_session_callback=None):
        self.obj = obj
        self.new_session_callback = new_session_callback
        self.close_session_callback = close_session_callback

    def get(self, *args, **kwargs):
        obj = self.obj
        if self.new_session_callback:
            obj = self.new_session_callback(self.obj)
        return ObjectDataHandler(obj, self.close_session_callback)

