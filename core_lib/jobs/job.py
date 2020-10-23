from abc import ABC, abstractmethod


class Job(ABC):

    def __init__(self):
        self.core_lib = None

    def set_core_lib(self, core_lib):
        self.core_lib = core_lib

    @abstractmethod
    def run(self):
        pass
