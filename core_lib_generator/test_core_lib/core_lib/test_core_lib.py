from omegaconf import DictConfig
from core_lib.core_lib import CoreLib

# template_cache_handler_imports
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from test_core_lib.core_lib.data_layers.data_access.user_data_access import UserDataAccess
from test_core_lib.core_lib.data_layers.data_access.customer_data_access import CustomerDataAccess
from test_core_lib.core_lib.data_layers.data.db.user import User
from test_core_lib.core_lib.data_layers.data.db.customer import Customer
# template_job_imports


class TemplateCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        # template_cache_handler
        user_db_session = SqlAlchemyDataHandlerRegistry(self.config.data.user_db)
        self.user = UserDataAccess(User, user_db_session)
        self.customer = CustomerDataAccess(Customer, user_db_session)
        # template_job_instances
