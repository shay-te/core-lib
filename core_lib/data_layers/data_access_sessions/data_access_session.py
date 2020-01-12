from abc import ABC, abstractmethod


class DataAccessSession(ABC):

    def __init__(self, session_name):
        self.session_name = session_name

    def get_name(self):
        self.session_name

    @abstractmethod
    def get_session(self, params: dict):
        pass
