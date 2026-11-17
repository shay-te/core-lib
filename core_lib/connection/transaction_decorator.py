import inspect
from functools import wraps

from core_lib.connection.transaction_scope import TransactionScope


class Transaction(object):
    """Run the decorated function as ONE transaction: every connection a factory hands out while
    it runs is the same connection per factory, committed once when it returns and rolled back
    when it raises. A nested @Transaction() on the same thread joins the open one."""

    def __call__(self, func):
        if inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func) or inspect.isgeneratorfunction(func):
            raise ValueError(
                f'@Transaction() cannot wrap `{func.__qualname__}`: it returns before its body runs, '
                f'so the transaction would end first'
            )

        @wraps(func)
        def __wrapper(*args, **kwargs):
            if TransactionScope.current() is not None:
                return func(*args, **kwargs)  # already inside a transaction: join it
            scope = TransactionScope.begin()
            try:
                result = func(*args, **kwargs)
            except BaseException as error:
                scope.end(error)
                raise
            scope.end(None)
            return result

        return __wrapper
