from functools import wraps

from core_lib.connection.transaction_scope import TransactionScope
from core_lib.core_lib import CoreLib


class Transaction(object):
    """Run the decorated function as ONE transaction: every SQLAlchemy DataAccess call inside it uses
    one session per database, committed once when it returns and rolled back when it raises. A nested
    @Transaction() on the same thread joins the open one."""

    def __call__(self, func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            if CoreLib.transaction_registry.get() is not None:
                return func(*args, **kwargs)  # already inside a transaction: join it
            transaction_scope = TransactionScope()
            CoreLib.transaction_registry.register(transaction_scope)
            try:
                result = func(*args, **kwargs)
            except BaseException as error:
                CoreLib.transaction_registry.unregister()  # before the end: nothing that runs from here on is "inside"
                transaction_scope.end(error)
                raise
            CoreLib.transaction_registry.unregister()
            transaction_scope.end(None)
            return result

        return __wrapper
