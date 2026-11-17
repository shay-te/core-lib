import logging
import threading
from contextvars import ContextVar
from typing import Callable, Optional

from core_lib.connection.connection import Connection
from core_lib.connection.joined_connection import JoinedConnection

logger = logging.getLogger(__name__)

# The transaction open in the current thread / asyncio task; None outside @Transaction().
_CURRENT_SCOPE = ContextVar('core_lib_transaction_scope', default=None)


class TransactionScope(object):
    """One open transaction: one connection per factory, ended once, and the callbacks to run
    after it commits. It lives in a ContextVar, so each thread and task sees only its own; it is
    joined only from the thread that opened it, because asyncio.to_thread copies ContextVars
    into a worker thread and a SQLAlchemy Session is not thread-safe."""

    def __init__(self):
        self._thread_id = threading.get_ident()
        self._connections = {}  # factory -> (connection, resource), in join order
        self._on_commit = []
        self._token = None

    @staticmethod
    def current() -> Optional['TransactionScope']:
        scope = _CURRENT_SCOPE.get()
        if scope is None or scope._thread_id != threading.get_ident():
            return None
        return scope

    @staticmethod
    def begin() -> 'TransactionScope':
        scope = TransactionScope()
        scope._token = _CURRENT_SCOPE.set(scope)
        return scope

    def join(self, factory, create: Callable[[], Connection]) -> JoinedConnection:
        # `factory` is not annotated: importing ConnectionFactory here would be circular.
        # `create` is the factory's own `get()`, called only when this factory has no connection yet.
        if factory not in self._connections:
            connection = create()
            self._connections[factory] = (connection, connection.__enter__())
        connection, resource = self._connections[factory]
        return JoinedConnection(connection, resource)

    def on_commit(self, callback: Callable[[], None]):
        self._on_commit.append(callback)

    def end(self, error: Optional[BaseException]):
        _CURRENT_SCOPE.reset(self._token)  # first: nothing that runs from here on is "inside"
        if error is None:
            self._commit()
        else:
            self._rollback(error)

    def _commit(self):
        commit_error = None
        for connection, _ in self._connections.values():
            try:
                if commit_error is None:
                    connection.__exit__(None, None, None)
                else:
                    connection.__exit__(type(commit_error), commit_error, commit_error.__traceback__)
            except BaseException as error:
                if commit_error is None:
                    commit_error = error
                else:
                    logger.exception('rolling back %s after a failed commit failed', type(connection).__name__)
        if commit_error is not None:
            raise commit_error
        self._run_on_commit()

    def _rollback(self, error: BaseException):
        for connection, _ in self._connections.values():
            try:
                connection.__exit__(type(error), error, error.__traceback__)
            except BaseException:
                logger.exception('rollback of %s failed', type(connection).__name__)

    def _run_on_commit(self):
        first_error = None
        for callback in self._on_commit:
            try:
                callback()
            except BaseException as error:
                if first_error is None:
                    first_error = error
                else:
                    logger.exception('an after-commit callback failed')
        if first_error is not None:
            raise first_error
