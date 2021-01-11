from core_lib.data_layers.data.handler.sql_alchemy_data_handler_factory import SqlAlchemyDataHandlerFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator


class TemplateCRUDDataAccess(CRUDSoftDataAccess):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerFactory, rule_validator: RuleValidator):
        CRUD.__init__(self, db_entity, db, rule_validator)
