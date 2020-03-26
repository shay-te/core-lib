from typing import List

from core_lib.observer.observer_listener import ObserverListener


class Observer(object):

    _listener: List[ObserverListener] = []

    def attach(self, listener: ObserverListener) -> None:
        self._listener.append(listener)

    def detach(self, listener: ObserverListener) -> None:
        self._listener.remove(listener)

    def notify(self, key: str, value) -> None:
        for observer in self._listener:
            observer.update(key, value)
