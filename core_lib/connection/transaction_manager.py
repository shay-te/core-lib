import logging
from typing import Optional

from core_lib.connection.transaction_scope import TransactionScope
from core_lib.connection.transactional_connection import TransactionalConnection
from core_lib.connection.transactional_connection_factory import TransactionalConnectionFactory
from core_lib.core_lib import CoreLib

logger = logging.getLogger(__name__)


class TransactionManager(object):
    """What a transaction does with its `TransactionScope`: hand out its connections and end them."""

    @staticmethod
    def get_connection(connection_factory: TransactionalConnectionFactory) -> TransactionalConnection:
        # outside a transaction: a new connection, as before; inside one: the transaction's connection for this
        # factory, created and marked `in_transaction` at its first use (the transaction ends it once, in `end`)
        transaction_scope = CoreLib.transaction_scope_registry.get()
        if transaction_scope is None:
            return connection_factory.create_connection()
        connection = transaction_scope.connections.get(connection_factory)
        if connection is None:
            connection = connection_factory.create_connection()
            connection.in_transaction = True
            transaction_scope.connections[connection_factory] = connection
        return connection

    @staticmethod
    def end(transaction_scope: TransactionScope, error: Optional[BaseException]) -> None:
        # commit every connection, or roll each back when `error` is set; a failed commit rolls back the rest and is
        # raised, a failed rollback is logged so the rest still end and the caller's own error is the one raised
        failure = error
        for connection in transaction_scope.connections.values():
            try:
                if failure is None:
                    connection.end(None, None, None)
                else:
                    connection.end(type(failure), failure, failure.__traceback__)
            except BaseException as end_error:  # NOSONAR - an interrupt must not skip ending the other connections
                if failure is None:
                    failure = end_error
                else:
                    logger.exception('rolling back %s failed', type(connection).__name__)
        if failure is None:
            TransactionManager._run_on_commit(transaction_scope)
        elif error is None:
            raise failure  # the commit failed (the caller's own error is raised by @Transaction())

    @staticmethod
    def _run_on_commit(transaction_scope: TransactionScope) -> None:
        # the data is committed: every callback runs, so one failing cache delete never leaves the next keys stale;
        # the first error is raised once all ran, the later ones are logged
        first_error = None
        for callback in transaction_scope.on_commit:
            try:
                callback()
            except BaseException as callback_error:  # NOSONAR - an interrupt must not skip the other callbacks
                if first_error is None:
                    first_error = callback_error
                else:
                    logger.exception('an after-commit callback failed')
        if first_error is not None:
            raise first_error
