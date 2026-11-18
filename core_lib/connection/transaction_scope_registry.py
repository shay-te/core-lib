import os
import threading
from typing import Optional

from core_lib.connection.transaction_scope import TransactionScope
from core_lib.registry.registry import Registry


class TransactionScopeRegistry(Registry):
    """The `TransactionScope` open on each thread. The key is always the calling thread, so a thread only ever
    gets its own: a worker thread (asyncio.to_thread included) is never inside its caller's transaction,
    because a SQLAlchemy Session is not thread-safe."""

    def __init__(self) -> None:
        self._thread_to_transaction_scope = {}
        # a forked child keeps the forking thread's id: without this it would find, and share, the parent's session
        if hasattr(os, 'register_at_fork'):  # not on Windows, which cannot fork
            os.register_at_fork(after_in_child=self._thread_to_transaction_scope.clear)

    def get(self) -> Optional[TransactionScope]:
        return self._thread_to_transaction_scope.get(threading.get_ident())

    def register(self, transaction_scope: TransactionScope) -> None:
        self._thread_to_transaction_scope[threading.get_ident()] = transaction_scope

    def unregister(self) -> None:
        del self._thread_to_transaction_scope[threading.get_ident()]
