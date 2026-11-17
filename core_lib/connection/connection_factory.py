from abc import ABC
from functools import partial, wraps

from core_lib.connection.transaction_scope import TransactionScope
from core_lib.factory.factory import Factory


class ConnectionFactory(Factory, ABC):
    """A subclass's `get()` builds a new connection per call. The base wraps it, so inside
    @Transaction() every call returns this factory's one connection for the transaction instead;
    only the first call's arguments create it (no core-lib factory reads them)."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'get' in cls.__dict__:
            cls.get = _join_transaction(cls.__dict__['get'])


def _join_transaction(get):
    @wraps(get)
    def __wrapper(self, *args, **kwargs):
        scope = TransactionScope.current()
        # Only the most-derived `get` joins: a `super().get()` inside it is what creates the connection.
        if scope is None or type(self).get is not __wrapper:
            return get(self, *args, **kwargs)
        return scope.join(self, partial(get, self, *args, **kwargs))

    return __wrapper
