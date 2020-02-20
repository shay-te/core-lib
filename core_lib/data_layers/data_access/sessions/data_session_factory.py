from abc import ABC, abstractmethod


class DataSessionFactory(ABC):

    @abstractmethod
    def get_session(self, name: str = None, params: dict = None):
        pass

