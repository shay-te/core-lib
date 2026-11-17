from abc import ABC, abstractmethod

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.transaction_scope import TransactionScope
from core_lib.connection.transactional_connection import TransactionalConnection


class TransactionalConnectionFactory(ConnectionFactory, ABC):
    """A connection factory whose connections can be part of @Transaction(). Subclass it and implement
    `create_connection`; `get` is done here: outside a transaction a new connection, inside one the
    transaction's one connection for this factory. Factories that are equal (`==`) share that connection."""

    def get(self, *args, **kwargs) -> TransactionalConnection:
        return TransactionScope.get(self)

    @abstractmethod
    def create_connection(self) -> TransactionalConnection:
        """A new connection, every call."""
        pass
