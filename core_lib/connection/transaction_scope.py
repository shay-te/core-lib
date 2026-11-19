from dataclasses import dataclass, field
from typing import Callable, Dict, List

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.transactional_connection import TransactionalConnection


@dataclass(eq=False)  # compared by identity: two open transactions are never "equal"
class TransactionScope(object):
    """One open transaction's data. `TransactionManager` holds the logic that uses it;
    `CoreLib.transaction_scope_registry` stores which one is open on each thread."""

    # connection factory -> its connection, in join order; keyed by the factory itself, so `==` (its identity())
    # decides, never the hash number alone
    connections: Dict[ConnectionFactory, TransactionalConnection] = field(default_factory=dict)
    on_commit: List[Callable[[], None]] = field(default_factory=list)   # run in order after the commit
