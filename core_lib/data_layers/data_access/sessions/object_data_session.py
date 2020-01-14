from core_lib.data_layers.data_access.sessions.data_session import DataSession


# this is the most simple "DataSession" it will always return the same object
class ObjectDataSession(DataSession):
    def __init__(self, name: str, obj: object):
        DataSession.__init__(self, name)
        self.obj = obj

    def get_name(self):
        return self.name

    def get_session(self, params: dict):
        return self.obj
