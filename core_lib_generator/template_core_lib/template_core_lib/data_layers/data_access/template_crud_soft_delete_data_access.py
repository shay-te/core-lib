from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator


class TemplateCRUDSoftDeleteDataAccess(CRUDSoftDeleteDataAccess):
    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator = None):
        CRUD.__init__(self, db_entity, db, rule_validator)
