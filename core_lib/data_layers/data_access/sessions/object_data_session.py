from core_lib.data_layers.data_access.sessions.data_session import DataSession


class ObjectDataSession(DataSession):

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj

    def __exit__(self, type, value, traceback):
        pass
