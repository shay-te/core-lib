from core_lib.connection.connection import Connection


class ObjectConnection(Connection):
    def __init__(self, obj, close_callback):
        self.obj = obj
        self.close_callback = close_callback

    def __enter__(self):
        return self.obj

    def __exit__(self, type, value, traceback):
        if self.close_callback:
            self.close_callback(self.obj)
