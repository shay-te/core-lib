from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_factory import SqlAlchemyDataHandlerFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.error_handling.decorators import NotFoundErrorHandler
from core_lib.rule_validator.rule_validator import RuleValidator


class CRUDDataAccess(DataAccess, CRUD):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerFactory, rule_validator: RuleValidator):
        CRUD.__init__(self, db_entity, db, rule_validator)

    @NotFoundErrorHandler()
    def get(self, id: int):
        assert id
        with self._db.get() as session:
            return session.query(self._db_entity).get(id)

    def delete(self, id: int):
        assert id
        with self._db.get() as session:
            session.query(self._db_entity).filter(self._db_entity.id == id).delete()
