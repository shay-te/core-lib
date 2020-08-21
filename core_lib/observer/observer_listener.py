from abc import ABC, abstractmethod


class ObserverListener(ABC):

    @abstractmethod
    def update(self, key: str, value):
        pass

