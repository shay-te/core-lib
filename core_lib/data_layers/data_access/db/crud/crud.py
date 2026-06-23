from abc import ABC, abstractmethod

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.rule_validator.rule_validator import RuleValidator


class CRUD(ABC):
    def __init__(self, db_entity, db: SqlAlchemyConnectionFactory, rule_validator: RuleValidator = None):
        self._db_entity = db_entity
        self._db = db
        self._rule_validator = rule_validator

    @abstractmethod
    def get(self, id: int):
        """
        Retrieve an entity by its ID.
        """
        pass

    def update(self, id: int, data: dict):
        # Use explicit raises (not `assert`) so `python -O` doesn't strip the
        # validation. Keep AssertionError to preserve the historical contract.
        """
        Update a database entity record by its ID with the provided data.
        
        The 'id' field is excluded from the update payload to prevent modification of the primary key.
        """
        if not id:
            raise AssertionError('CRUD.update requires a truthy `id`')
        if not data:
            raise AssertionError('CRUD.update requires non-empty `data`')
        updated_data = self._rule_validator.validate_dict(data) if self._rule_validator else data
        # Drop `id` from the update payload — UPDATE-ing the primary key is
        # rarely intended and breaks foreign-key relations. Makes update()
        # consistent with create() which already excludes `id`.
        updated_data = {k: v for k, v in updated_data.items() if k != 'id'}
        with self._db.get() as session:
            session.query(self._db_entity).filter(self._db_entity.id == id).update(updated_data)

    def create(self, data: dict):
        """
        Create and persist a new entity from the provided data.
        
        Parameters:
        	data (dict): Field values to assign to the new entity.
        
        Returns:
        	entity: The newly created entity.
        """
        if not data:
            raise AssertionError('CRUD.create requires non-empty `data`')
        updated_data = self._rule_validator.validate_dict(data, strict_mode=False) if self._rule_validator else data
        with self._db.get() as session:
            entity = self._db_entity()
            for key, value in updated_data.items():
                if key != 'id' and hasattr(entity, key):
                    setattr(entity, key, value)

            session.add(entity)
        return entity

    @abstractmethod
    def delete(self, id: int):
        pass
