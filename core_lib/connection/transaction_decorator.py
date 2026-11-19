import inspect
import logging
from functools import wraps
from typing import Any, Callable

from core_lib.connection.transaction_manager import TransactionManager
from core_lib.connection.transaction_scope import TransactionScope
from core_lib.core_lib import CoreLib

logger = logging.getLogger(__name__)


class Transaction(object):
    """Run the decorated function as ONE transaction: every SQLAlchemy DataAccess call inside it uses
    one session per database, committed once when it returns and rolled back when it raises. A nested
    @Transaction() on the same thread joins the open one. Decorate a plain `def`: see the warning below."""

    def __call__(self, func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func) or inspect.isgeneratorfunction(func):
            # calling it only builds a coroutine or generator: the transaction would end before the body runs
            logger.warning('@Transaction() on `%s` does nothing: an async function or a generator runs its body '
                           'after the transaction ended. Decorate a plain `def`.', func.__qualname__)

        @wraps(func)
        def __wrapper(*args, **kwargs) -> Any:
            if CoreLib.transaction_scope_registry.get() is not None:
                return func(*args, **kwargs)  # already inside a transaction: join it
            transaction_scope = TransactionScope()
            CoreLib.transaction_scope_registry.register(transaction_scope)
            try:
                result = func(*args, **kwargs)
            except BaseException as error:
                # before the end: nothing that runs from here on is "inside"
                CoreLib.transaction_scope_registry.unregister()
                TransactionManager.end(transaction_scope, error)
                raise
            CoreLib.transaction_scope_registry.unregister()
            TransactionManager.end(transaction_scope, None)
            return result

        return __wrapper
