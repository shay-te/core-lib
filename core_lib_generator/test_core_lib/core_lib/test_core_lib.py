from omegaconf import DictConfig
from core_lib.core_lib import CoreLib

# template_cache_handler_imports
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from test_core_lib.core_lib.data_layers.data_access.DetailsDataAccess import Detailsdataaccess
from test_core_lib.core_lib.data_layers.data_access.CustDetailsDataAccess import Custdetailsdataaccess
# template_entity_imports
# template_job_imports


class TemplateCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        # template_cache_handler
        customer_data_session = SqlAlchemyDataHandlerRegistry(self.config.data.customer_data)
        user_data_session = SqlAlchemyDataHandlerRegistry(self.config.data.user_data)
        self.details = Detailsdataaccess(Details, user_data_session)
        self.details = Custdetailsdataaccess(Details, customer_data_session)
        # template_job_instances
