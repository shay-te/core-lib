from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator
from facebook_core_lib.core_lib.data_layers.data.sellerdb.entities.data import Data


class SellerDataAccess(CRUDDataAccess):
    def __init__(self, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator = None):
        CRUD.__init__(self, Data, db, rule_validator)
