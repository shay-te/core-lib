import logging
import threading
from typing import List

from core_lib.observer.observer_listener import ObserverListener


logger = logging.getLogger(__name__)


class Observer(object):
    def __init__(self, listener: ObserverListener = None, listener_type: object = None):
        """
        Initialize an Observer instance for managing listener notifications.
        
        Parameters:
        	listener (ObserverListener, optional): Initial listener to attach during initialization.
        	listener_type (object, optional): Type constraint for listeners. All attached listeners must be instances of this type.
        """
        self._listener: List[ObserverListener] = []
        self._listener_type = listener_type
        # Protect attach/detach/notify against concurrent mutation. Without
        # this lock a listener detaching during a notify could cause weird
        # iteration behavior on the underlying list.
        self._lock = threading.RLock()
        if listener:
            self.attach(listener)

    def attach(self, listener: ObserverListener) -> None:
        """
        Attach a listener to the observer.
        
        Raises:
            AssertionError: If the listener is None or does not match the configured listener type.
        """
        self._validate(listener)
        with self._lock:
            self._listener.append(listener)

    def detach(self, listener: ObserverListener) -> None:
        """
        Remove a registered listener from this observer.
        
        Parameters:
            listener (ObserverListener): The listener to remove.
        
        Raises:
            ValueError: If the listener is not registered.
            AssertionError: If the listener is None or not an instance of the configured listener type.
        """
        self._validate(listener)
        with self._lock:
            self._listener.remove(listener)

    def notify(self, key: str, value) -> None:
        # Snapshot the listener list under the lock, then iterate the
        # snapshot outside the lock so listeners can safely attach/detach
        # other listeners during dispatch without deadlocking.
        """
        Notify all registered listeners of an update to the specified key.
        
        If any listener raises an exception during update, the exception is logged and re-raised.
        
        Parameters:
            key (str): The identifier of the value being updated.
            value: The new value associated with the key.
        """
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
        """
        Validates that a listener is not None and matches the configured listener type if one is set.
        
        Parameters:
        	listener (ObserverListener): The listener to validate
        
        Raises:
        	AssertionError: If the listener is None or does not match the configured listener type
        """
        if not listener:
            raise AssertionError('ObserverListener cannot be None')
        if self._listener_type and not isinstance(listener, self._listener_type):
            raise AssertionError(
                f'ObserverListener must be of type `{self._listener_type}`'
            )
