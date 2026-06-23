from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler
from core_lib.rule_validator.rule_validator import RuleValidator


class CRUDDataAccess(DataAccess, CRUD):
    def __init__(self, db_entity, db: SqlAlchemyConnectionFactory, rule_validator: RuleValidator = None):
        CRUD.__init__(self, db_entity, db, rule_validator)

    @NotFoundErrorHandler()
    def get(self, id: int):
        """
        Retrieve an entity by its ID.
        
        Parameters:
            id (int): The ID of the entity to retrieve. Must be truthy.
        
        Returns:
            The entity with the specified ID, or None if not found.
        
        Raises:
            AssertionError: If `id` is falsy.
        """
        if not id:
            raise AssertionError('CRUDDataAccess.get requires a truthy `id`')
        with self._db.get() as session:
            return session.query(self._db_entity).get(id)

    def delete(self, id: int):
        """
        Delete the record with the specified ID.
        
        Returns:
        	int: The number of rows deleted.
        
        Raises:
        	AssertionError: If id is falsy.
        """
        if not id:
            raise AssertionError('CRUDDataAccess.delete requires a truthy `id`')
        with self._db.get() as session:
            return session.query(self._db_entity).filter(self._db_entity.id == id).delete()
