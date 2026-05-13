from datetime import datetime, timezone

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler
from core_lib.rule_validator.rule_validator import RuleValidator


class CRUDSoftDeleteWithTokenDataAccess(DataAccess, CRUD):
    def __init__(self, db_entity, db: SqlAlchemyConnectionFactory, rule_validator: RuleValidator = None):
        CRUD.__init__(self, db_entity, db, rule_validator)

    @NotFoundErrorHandler()
    def get(self, id: int):
        if not id:
            raise AssertionError('CRUDSoftDeleteWithTokenDataAccess.get requires a truthy `id`')
        with self._db.get() as session:
            return (
                session.query(self._db_entity)
                .filter(self._db_entity.id == id, self._db_entity.deleted_at_token == 0)
                .first()
            )

    def delete(self, id: int):
        if not id:
            raise AssertionError('CRUDSoftDeleteWithTokenDataAccess.delete requires a truthy `id`')
        # Compute deletion time once to avoid TOCTOU drift between the
        # datetime column and the integer token (both must encode the
        # same instant).  Use timezone-aware UTC: datetime.utcnow().timestamp()
        # interprets naive UTC as local time, producing an incorrect epoch
        # on non-UTC systems.
        now = datetime.now(tz=timezone.utc)
        with self._db.get() as session:
            return (
                session.query(self._db_entity)
                .filter(self._db_entity.id == id)
                .update(
                    {
                        self._db_entity.deleted_at: now.replace(tzinfo=None),
                        self._db_entity.deleted_at_token: int(now.timestamp()),
                    }
                )
            )
