from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import (
    CRUDSoftDeleteWithTokenDataAccess,
)
from core_lib.rule_validator.rule_validator import RuleValidator
from facebook_core_lib.core_lib.data_layers.data.userdb.entities.details import Details


class DetailsDataAccess(CRUDSoftDeleteWithTokenDataAccess):
    def __init__(self, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator = None):
        CRUD.__init__(self, Details, db, rule_validator)
