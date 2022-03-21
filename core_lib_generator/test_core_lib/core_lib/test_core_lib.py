from omegaconf import DictConfig
from core_lib.core_lib import CoreLib

# template_cache_handler_imports
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from test_core_lib.core_lib.data_layers.data_access.details_data_access import DetailsDataAccess
from test_core_lib.core_lib.data_layers.data_access.cust_details_data_access import CustDetailsDataAccess
# template_entity_imports
# template_job_imports


class TemplateCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        # template_cache_handler
        user_data_session = SqlAlchemyDataHandlerRegistry(self.config.data.user_data)
        customer_data_session = SqlAlchemyDataHandlerRegistry(self.config.data.customer_data)
        self.details = DetailsDataAccess(Details, user_data_session)
        self.details = CustDetailsDataAccess(Details, customer_data_session)
        # template_job_instances
