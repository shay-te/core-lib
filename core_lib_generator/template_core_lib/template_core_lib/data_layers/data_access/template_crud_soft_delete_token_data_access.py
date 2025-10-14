from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import (
    CRUDSoftDeleteWithTokenDataAccess,
)
from core_lib.rule_validator.rule_validator import RuleValidator
# template_function_imports
# template_entity_imports


class Template(CRUDSoftDeleteWithTokenDataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory, rule_validator: RuleValidator = None):
        CRUD.__init__(self, db_entity, db, rule_validator)
# template_functions
