from sqlalchemy import select

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator
from tests.test_data.transaction_widget import TransactionWidget

allowed_update_types = [
    ValueRuleValidator(TransactionWidget.group_id.key, int),
    ValueRuleValidator(TransactionWidget.name.key, str),
]
rule_validator = RuleValidator(allowed_update_types)


class TransactionWidgetDataAccess(CRUDDataAccess):
    """Ordinary DataAccess queries, written exactly as outside a transaction: no session parameter."""

    def __init__(self, db: SqlAlchemyConnectionFactory):
        CRUD.__init__(self, TransactionWidget, db, rule_validator)

    def delete_group(self, group_id: int) -> int:
        with self._db.get() as session:
            return session.query(TransactionWidget).filter(TransactionWidget.group_id == group_id).delete()

    def names_in_group(self, group_id: int) -> list:
        with self._db.get() as session:
            return session.execute(
                select(TransactionWidget.name)
                .where(TransactionWidget.group_id == group_id)
                .order_by(TransactionWidget.name)
            ).scalars().all()

    def count_all(self) -> int:
        with self._db.get() as session:
            return session.query(TransactionWidget).count()

    def current_session(self):
        # Test-only: hands out the block's session so tests can compare session identity.
        with self._db.get() as session:
            return session

    def raise_inside_block(self, message: str):
        with self._db.get():
            raise ValueError(message)
