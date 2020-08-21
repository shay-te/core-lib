from abc import abstractmethod, ABC


class TokenHandler(ABC):

    @abstractmethod
    def encode(self, message: dict):
        pass

    @abstractmethod
    def decode(self, encoded):
        pass
