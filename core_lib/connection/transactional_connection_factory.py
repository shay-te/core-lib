from abc import ABC, abstractmethod

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.transactional_connection import TransactionalConnection


class TransactionalConnectionFactory(ConnectionFactory, ABC):
    """A connection factory whose connections can be part of @Transaction(). Subclass it and implement
    `create_connection` and `identity`; `get`, `__eq__` and `__hash__` are done here: outside a transaction `get`
    returns a new connection, inside one the transaction's one connection for every factory with this identity."""

    def get(self, *args, **kwargs) -> TransactionalConnection:
        """Takes no arguments (the signature is `Factory.get`'s): every connection comes from `create_connection()`,
        built from the factory's own configuration."""
        # imported here, not at the top: TransactionManager imports this class for its type hints
        from core_lib.connection.transaction_manager import TransactionManager
        return TransactionManager.get_connection(self)

    def __eq__(self, other: object) -> bool:
        # factories with the same identity share one connection inside a transaction
        return isinstance(other, TransactionalConnectionFactory) and other.identity() == self.identity()

    def __hash__(self) -> int:
        return hash(self.identity())

    @abstractmethod
    def create_connection(self) -> TransactionalConnection:
        """A new connection, every call."""
        pass

    @abstractmethod
    def identity(self) -> str:
        """Names what this factory's connections reach. Factories with the same identity share one connection inside
        a transaction. Never put a secret in it: it is a plain string anyone may print."""
        pass
