from abc import ABC, abstractmethod


# Make `__enter__` and `__exit__` to hint the user of the factory use
class Connection(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback):
        pass

    def flush(self):
        """Push this block's writes to the backend without ending the transaction. Called by
        JoinedConnection when a `with` block ends inside @Transaction(); a backend with nothing to
        push keeps this no-op."""
        pass
