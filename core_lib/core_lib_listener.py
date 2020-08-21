from abc import ABC, abstractmethod


class CoreLibListener(ABC):

    @abstractmethod
    def on_core_lib_ready(self):
        pass
