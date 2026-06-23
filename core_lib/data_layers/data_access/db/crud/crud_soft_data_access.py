from datetime import datetime

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler
from core_lib.rule_validator.rule_validator import RuleValidator


class CRUDSoftDeleteDataAccess(DataAccess, CRUD):
    def __init__(self, db_entity, db: SqlAlchemyConnectionFactory, rule_validator: RuleValidator = None):
        CRUD.__init__(self, db_entity, db, rule_validator)

    @NotFoundErrorHandler()
    def get(self, id: int):
        """
        Retrieve a single entity by ID, excluding soft-deleted records.
        
        Parameters:
            id (int): The entity ID. Must be truthy.
        
        Returns:
            The entity with the given ID if found and not soft-deleted, or None.
        
        Raises:
            AssertionError: If id is falsy.
        """
        if not id:
            raise AssertionError('CRUDSoftDeleteDataAccess.get requires a truthy `id`')
        with self._db.get() as session:
            return (
                session.query(self._db_entity)
                # Use `.is_(None)` (the SQLAlchemy idiom for `IS NULL`) so
                # linters don't flag `== None` while still emitting the
                # same SQL.
                .filter(self._db_entity.id == id, self._db_entity.deleted_at.is_(None))
                .first()
            )

    def delete(self, id: int):
        """
        Soft-deletes a record by marking it as deleted.
        
        Parameters:
            id (int): The record identifier. Must be a truthy value.
        
        Returns:
            The number of rows affected by the update.
        
        Raises:
            AssertionError: If id is falsy.
        """
        if not id:
            raise AssertionError('CRUDSoftDeleteDataAccess.delete requires a truthy `id`')
        with self._db.get() as session:
            return (
                session.query(self._db_entity)
                .filter(self._db_entity.id == id)
                .update({self._db_entity.deleted_at: datetime.utcnow()})
            )
