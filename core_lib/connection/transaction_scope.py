import logging
from typing import TYPE_CHECKING, Callable, Optional

from core_lib.connection.transactional_connection import TransactionalConnection
from core_lib.core_lib import CoreLib

if TYPE_CHECKING:
    # for the type hints only: the factory's `get()` calls this scope, so importing it at runtime would be circular
    from core_lib.connection.transactional_connection_factory import TransactionalConnectionFactory

logger = logging.getLogger(__name__)


class TransactionScope(object):
    """One open transaction: one connection per factory, ended once, and the callbacks to run after
    it commits. Which transaction is open on a thread is stored in `CoreLib.transaction_registry`."""

    def __init__(self):
        # connection factory -> its connection, in the order they joined. Keyed by the factory itself, not by its
        # hash: the dict compares keys with `==` too, so two in-memory sqlite engines (same URL, same hash, two
        # databases) stay separate while two factories on one database share a connection.
        self._connections = {}
        self._on_commit = []

    @staticmethod
    def get(connection_factory: 'TransactionalConnectionFactory') -> TransactionalConnection:
        # The connection a factory's `get()` hands out. Outside a transaction: a new one, as before. Inside one:
        # the transaction's one connection for this factory, created at its first use. While `in_transaction` is
        # True the end of a block only flushes it: the transaction ends it once, in `end`
        transaction_scope = CoreLib.transaction_registry.get()
        if transaction_scope is None:
            return connection_factory.create_connection()
        connection = transaction_scope._connections.get(connection_factory)
        if connection is None:
            connection = connection_factory.create_connection()
            connection.in_transaction = True
            transaction_scope._connections[connection_factory] = connection
        return connection

    def on_commit(self, callback: Callable[[], None]):
        self._on_commit.append(callback)

    def end(self, error: Optional[BaseException]):
        # Commit every connection, or roll every one back when `error` is set. A failed commit rolls back
        # the connections after it and is raised; a failed rollback is logged, so the rest still end and
        # the caller's own error is the one raised.
        failure = error
        for connection in self._connections.values():
            try:
                if failure is None:
                    connection.end(None, None, None)
                else:
                    connection.end(type(failure), failure, failure.__traceback__)
            except BaseException as end_error:
                if failure is None:
                    failure = end_error
                else:
                    logger.exception('rolling back %s failed', type(connection).__name__)
        if failure is None:
            for callback in self._on_commit:
                callback()
        elif error is None:
            raise failure  # the commit failed (the caller's own error is raised by @Transaction())
