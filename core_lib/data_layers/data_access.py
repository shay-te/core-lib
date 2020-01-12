from core_lib.single_instance import SingleInstance


class DataAccess(SingleInstance):

    __instances = []

    def __init__(self, sessions):
        self.sessions = sessions

    def __new__(cls, *args, **kwargs):
        instance = super(SingleInstance, cls).__new__(cls)
        DataAccess.__instances.append(instance)
        return instance

    def get_session(self, name: str, params: dict):
        self.sessions[name].