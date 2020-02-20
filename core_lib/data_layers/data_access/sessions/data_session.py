from abc import ABC, abstractmethod


# This class is used by the "DataAccess"
# the method "DataAccess.get_session" will fetch the desired "DataAccess" class
# and will call the "get_session" method
class DataSession(ABC):

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback):
        pass
