from core_lib.connection.connection import Connection


class JoinedConnection(Connection):
    """What `ConnectionFactory.get()` returns inside `@Transaction()`: the transaction's one
    connection, without its end. A block that ends cleanly only flushes; the commit or rollback,
    and the close, belong to the transaction and happen once, when it ends."""

    def __init__(self, connection: Connection, resource):
        self._connection = connection
        self._resource = resource

    def __enter__(self):
        return self._resource

    def __exit__(self, exec_type, exec_value, traceback):
        if exec_type is None:
            self._connection.flush()
        return False  # never swallow: an exception goes up to the transaction, which rolls back
