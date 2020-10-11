from abc import ABC, abstractmethod


class Job(ABC):

    def __init__(self, *args, **kwargs):
        self.core_lib = kwargs.get('core_lib')

    @abstractmethod
    def run(self):
        pass
