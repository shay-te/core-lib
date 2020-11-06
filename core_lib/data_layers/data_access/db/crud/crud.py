from abc import ABC, abstractmethod

from core_lib.data_layers.data.handler.sql_alchemy_data_handler_factory import SqlAlchemyDataHandlerFactory
from core_lib.rule_validator.rule_validator import RuleValidator


class CRUD(ABC):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerFactory, rule_validator: RuleValidator):
        self._db_entity = db_entity
        self._db = db
        self._rule_validator = rule_validator

    @abstractmethod
    def get(self, id: int):
        pass

    def update(self, id: int, data: dict):
        assert id and data
        if self._rule_validator:
            self._rule_validator.validate_dict(data)
        with self._db.get() as session:
            session.query(self._db_entity).filter(self._db_entity.id == id).update(data)

    def create(self, data: dict):
        assert data
        if self._rule_validator:
            self._rule_validator.validate_dict(data, strict_mode=False)
        with self._db.get() as session:
            entity = self._db_entity()
            for key, value in data.items():
                if key != 'id' and hasattr(entity, key):
                    setattr(entity, key, value)

            session.add(entity)
        return entity

    @abstractmethod
    def delete(self, id: int):
        pass
