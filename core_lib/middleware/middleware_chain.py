import logging
from typing import Any, List
from core_lib.middleware.middleware import Middleware

logger = logging.getLogger(__name__)


class MiddlewareChain:
    def __init__(self):
        self._middlewares: List[Middleware] = []

    def add(self, middleware: Middleware):
        self._middlewares.append(middleware)

    def remove(self, middleware: Middleware):
        if middleware in self._middlewares:
            self._middlewares.remove(middleware)

    def clear(self):
        self._middlewares.clear()

    def execute(self, context: Any):
        for mw in self._middlewares:
            mw.handle(context)

