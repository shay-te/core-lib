from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Optional, Type

from core_lib.connection.connection import Connection


class TransactionalConnection(Connection, ABC):
    """A connection that can be part of @Transaction(). Subclass it for a backend with real transactions and
    implement `open`, `flush`, `release` and `end`; `__enter__` and `__exit__` are done here.

    Outside a transaction, the end of every `with` block ends the connection (`end`). Inside one, `in_transaction`
    is True: a block that ends cleanly calls `flush`, the last open block to end calls `release`, and the transaction
    calls `end` once, when it ends."""

    in_transaction = False  # set by TransactionManager while the transaction holds this connection
    open_blocks = 0         # the `with` blocks using this connection right now (a block may open inside another)

    def __enter__(self) -> Any:
        self.open_blocks += 1
        return self.open()

    def __exit__(self, exec_type: Optional[Type[BaseException]], exec_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        # returns None, so an error in the block goes up; inside a transaction, its end rolls back through `end`
        self.open_blocks -= 1
        if not self.in_transaction:
            self.end(exec_type, exec_value, traceback)
        else:
            if exec_type is None:
                self.flush()
            if self.open_blocks == 0:
                self.release()

    @abstractmethod
    def open(self) -> Any:
        """What the `with` block gets: the session, the client."""
        pass

    @abstractmethod
    def flush(self) -> None:
        """Send the block's pending writes without committing them."""
        pass

    @abstractmethod
    def release(self) -> None:
        """The last open block ended: let go of what the blocks loaded and drop the writes they did not send, as
        the end of a block outside a transaction does."""
        pass

    @abstractmethod
    def end(self, exec_type: Optional[Type[BaseException]], exec_value: Optional[BaseException],
            traceback: Optional[TracebackType]) -> None:
        """End the connection: commit when `exec_type` is None, roll back otherwise; then close it."""
        pass
