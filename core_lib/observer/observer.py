from typing import List

from core_lib.observer.observer_listener import ObserverListener


class Observer(object):

    def __init__(self, listener: ObserverListener = None, listener_type: object = None):
        self._listener: List[ObserverListener] = []
        self._listener_type = listener_type
        if listener:
            self.attach(listener)

    def attach(self, listener: ObserverListener) -> None:
        self._validate(listener)
        self._listener.append(listener)

    def detach(self, listener: ObserverListener) -> None:
        self._validate(listener)
        self._listener.remove(listener)

    def notify(self, key: str, value) -> None:
        for observer in self._listener:
            observer.update(key, value)

    def _validate(self, listener: ObserverListener):
        assert listener, 'ObserverListener cannot be None'
        if self._listener_type:
            assert isinstance(listener, self._listener_type), 'ObserverListener must be of type `{}`'.format(self._listener_type)
