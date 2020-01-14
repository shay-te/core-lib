from abc import ABC, abstractmethod


# This class is used by the "DataAccess"
# the method "DataAccess.get_session" will fetch the desired "DataAccess" class
# and will call the "get_session" method
class DataSession(ABC):

    def __init__(self, session_name):
        self.session_name = session_name

    def get_name(self):
        return self.session_name

    @abstractmethod
    def get_session(self, params: dict):
        pass
