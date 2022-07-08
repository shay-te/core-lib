import pysolr
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib
from core_lib.data_layers.data.data_helpers import build_url

from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry
from core_lib.connection.object_connection_registry import ObjectConnectionRegistry
from examples.demo_core_lib.core_lib.data_layers.data_access.demo_data_access import DemoDataAccess
from examples.demo_core_lib.core_lib.data_layers.data_access.demo_search_data_access import DemoSearchDataAccess
from examples.demo_core_lib.core_lib.data_layers.service.demo_search_service import DemoSearchService
from examples.demo_core_lib.core_lib.data_layers.service.demo_service import DemoService


class DemoCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf.core_lib

        db_data_session = SqlAlchemyConnectionRegistry(self.config.db)
        solr_data_session = ObjectConnectionRegistry(pysolr.Solr(build_url(**self.config.solr), always_commit=True))

        self.info = DemoService(DemoDataAccess(db_data_session))
        self.search = DemoSearchService(DemoSearchDataAccess(solr_data_session))
