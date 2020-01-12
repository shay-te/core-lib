from core_lib.single_instance import SingleInstance


class DataAccess(SingleInstance):

    __instances = []

    def __init__(self, sessions: dict):
        self.sessions = sessions

    def __new__(cls, *args, **kwargs):
        instance = super(SingleInstance, cls).__new__(cls)
        DataAccess.__instances.append(instance)
        return instance

    def get_session(self, name: str, params: dict):
        if not name and self.sessions:
            session = next(iter(self.sessions.values()))
        else:
            session = self.sessions[name].get_session(params)

        return session.get_session(params)
