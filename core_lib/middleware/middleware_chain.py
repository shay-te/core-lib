import logging
import threading
from typing import Any, List
from core_lib.middleware.middleware import Middleware

logger = logging.getLogger(__name__)


class MiddlewareChain:
    def __init__(self):
        """
        Initialize an empty middleware chain with a re-entrant lock for thread-safe synchronization.
        """
        self._middlewares: List[Middleware] = []
        # Guard mutation and iteration so a middleware can safely
        # add/remove other middlewares during execute().
        self._lock = threading.RLock()

    def add(self, middleware: Middleware):
        """
        Adds a middleware to the chain.
        """
        with self._lock:
            self._middlewares.append(middleware)

    def remove(self, middleware: Middleware):
        """
        Remove a middleware from the chain.
        
        If the middleware is not registered, this operation has no effect.
        """
        with self._lock:
            if middleware in self._middlewares:
                self._middlewares.remove(middleware)

    def clear(self):
        """
        Clear all registered middlewares from the chain.
        """
        with self._lock:
            self._middlewares.clear()

    def execute(self, context: Any):
        # Iterate a snapshot so a middleware can mutate the chain during
        # dispatch without corrupting iteration.
        """
        Dispatch a context object through all registered middlewares in sequence.
        
        Each middleware's handle method is called with the context in registration order.
        Middlewares can safely add or remove other middlewares during dispatch without
        affecting the current execution.
        """
        with self._lock:
            snapshot = list(self._middlewares)
        for mw in snapshot:
            mw.handle(context)

