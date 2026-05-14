import logging
import threading
from typing import List

from core_lib.observer.observer_listener import ObserverListener


logger = logging.getLogger(__name__)


class Observer(object):
    def __init__(self, listener: ObserverListener = None, listener_type: object = None):
        self._listener: List[ObserverListener] = []
        self._listener_type = listener_type
        # Protect attach/detach/notify against concurrent mutation. Without
        # this lock a listener detaching during a notify could cause weird
        # iteration behavior on the underlying list.
        self._lock = threading.RLock()
        if listener:
            self.attach(listener)

    def attach(self, listener: ObserverListener) -> None:
        self._validate(listener)
        with self._lock:
            self._listener.append(listener)

    def detach(self, listener: ObserverListener) -> None:
        self._validate(listener)
        with self._lock:
            self._listener.remove(listener)

    def notify(self, key: str, value) -> None:
        # Snapshot the listener list under the lock, then iterate the
        # snapshot outside the lock so listeners can safely attach/detach
        # other listeners during dispatch without deadlocking.
        with self._lock:
            snapshot = list(self._listener)
        for observer in snapshot:
            try:
                observer.update(key, value)
            except Exception as ex:
                # `logger.exception` automatically captures the traceback.
                # The previous `logger.error(msg, ex)` passed ex as a
                # %-format argument and triggered "not all arguments
                # converted" inside the logging machinery.
                logger.exception('error while Observer.notify on key: `%s`', key)
                raise ex

    def _validate(self, listener: ObserverListener):
        # Explicit raises (not `assert`) so `python -O` doesn't strip the
        # validation; preserve AssertionError for backwards compatibility.
        if not listener:
            raise AssertionError('ObserverListener cannot be None')
        if self._listener_type and not isinstance(listener, self._listener_type):
            raise AssertionError(
                f'ObserverListener must be of type `{self._listener_type}`'
            )
