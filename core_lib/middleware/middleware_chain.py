import logging
import threading
from typing import Any, List
from core_lib.middleware.middleware import Middleware

logger = logging.getLogger(__name__)


class MiddlewareChain:
    def __init__(self):
        self._middlewares: List[Middleware] = []
        # Guard mutation and iteration so a middleware can safely
        # add/remove other middlewares during execute().
        self._lock = threading.RLock()

    def add(self, middleware: Middleware):
        with self._lock:
            self._middlewares.append(middleware)

    def remove(self, middleware: Middleware):
        with self._lock:
            if middleware in self._middlewares:
                self._middlewares.remove(middleware)

    def clear(self):
        with self._lock:
            self._middlewares.clear()

    def execute(self, context: Any):
        # Iterate a snapshot so a middleware can mutate the chain during
        # dispatch without corrupting iteration.
        with self._lock:
            snapshot = list(self._middlewares)
        for mw in snapshot:
            mw.handle(context)

