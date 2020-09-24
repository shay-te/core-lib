from abc import ABC, abstractmethod


class Job(ABC):

    def __init__(self):
        self.core_lib = None

    # When run from configuration at startup, CoreLib will run this method with the running CoreLib instance
    def set_core_lib(self, core_lib):
        self.core_lib = core_lib

    @abstractmethod
    def run(self):
        pass
