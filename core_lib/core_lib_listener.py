import enum
from abc import ABC, abstractmethod

from core_lib.observer.observer_listener import ObserverListener


class CoreLibListener(ObserverListener):
    class CoreLibEventType(enum.Enum):
        CORE_LIB_READY = 'CORE_LIB_READY'

    @abstractmethod
    def on_core_lib_ready(self):
        pass

    def update(self, key: str, value):
        if key == CoreLibListener.CoreLibEventType.CORE_LIB_READY:
            self.on_core_lib_ready()

