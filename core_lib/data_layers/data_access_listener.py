from abc import ABC, abstractmethod


class DataAccessListener(ABC):

    @abstractmethod
    def on_core_lib_ready(self):
        pass
