from abc import ABC, abstractmethod


class Job(ABC):

    @abstractmethod
    def initialized(self, data_handler):
        pass

    def set_data_handler(self, data_handler):
        self.initialized(data_handler)

    @abstractmethod
    def run(self):
        pass
