from abc import ABC, abstractmethod


class Factory(ABC):

    @abstractmethod
    def get(self, *args, **kwargs):
        pass
