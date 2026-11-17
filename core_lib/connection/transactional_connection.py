from abc import ABC, abstractmethod

from core_lib.connection.connection import Connection


class TransactionalConnection(Connection, ABC):
    """A connection that can be part of @Transaction(). Subclass it for a backend with real transactions and
    implement `flush` and `end`; `__exit__` is done here.

    Outside a transaction, the end of every `with` block ends the connection (`end`). Inside one,
    `in_transaction` is True: a block only calls `flush`, and the transaction calls `end` once, when it ends."""

    in_transaction = False  # set by TransactionScope while it holds this connection

    def __exit__(self, exec_type, exec_value, traceback):
        if self.in_transaction:
            # an error does nothing here: it goes up, and the transaction's end rolls back through `end`
            if exec_type is None:
                self.flush()
            return False
        return self.end(exec_type, exec_value, traceback)

    @abstractmethod
    def flush(self):
        """Send the block's pending writes without committing them."""
        pass

    @abstractmethod
    def end(self, exec_type, exec_value, traceback):
        """End the connection: commit when `exec_type` is None, roll back otherwise; then close it."""
        pass
