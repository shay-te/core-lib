from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_factory import SqlAlchemyDataHandlerFactory
from core_lib.error_handling.decorators import NotFoundErrorHandler
from core_lib.rule_validator.rule_validator import RuleValidator


class CRUDDataAccess(DataAccess):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerFactory, rule_validator: RuleValidator):
        self._db_entity = db_entity
        self._db = db
        self._rule_validator = rule_validator

    @NotFoundErrorHandler()
    def get(self, id: int):
        with self._db.get() as session:
            return session.query(self._db_entity).get(id)

    def update(self, id: int, data: dict):
        if self._rule_validator:
            self.rule_validator.validate_dict(data)
        with self._db.get() as session:
            session.query(self._db_entity).filter(self._db_entity.id == id).update(data)

    def create(self, data: dict):
        if self._rule_validator:
            self.rule_validator.validate_dict(data)
        with self._db.get() as session:
            challenge = self._db_entity()
            for key, value in data.items():
                if key != 'id' and hasattr(challenge, key):
                    setattr(challenge, key, value)

            session.add(challenge)
        return challenge
