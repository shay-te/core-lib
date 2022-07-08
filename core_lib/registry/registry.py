from abc import ABC, abstractmethod


class Registry(ABC):

    @abstractmethod
    def get(self, *args, **kwargs):
        pass
