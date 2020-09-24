from abc import ABC, abstractmethod


# Make `__enter__` and `__exit__` to hint the user of the factory use
class DataHandler(ABC):

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback):
        pass
