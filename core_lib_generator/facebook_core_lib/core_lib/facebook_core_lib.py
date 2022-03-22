from omegaconf import DictConfig
from core_lib.core_lib import CoreLib

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from facebook_core_lib.core_lib.data_layers.data_access.details_data_access import DetailsDataAccess
from facebook_core_lib.core_lib.data_layers.data_access.data_data_access import DataDataAccess
from facebook_core_lib.core_lib.data_layers.data_access.seller_details_data_access import SellerDetailsDataAccess
from facebook_core_lib.core_lib.data_layers.data_access.seller_data_access import SellerDataAccess


class FacebookCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        CoreLib.cache_registry.register('memcached_cache', CacheHandlerMemcached(build_url(host=self.config.core_lib.facebook_core_lib.cache.url.host, port=self.config.core_lib.facebook_core_lib.cache.url.port)))
        sellerdb_session = SqlAlchemyDataHandlerRegistry(self.config.core_lib.facebook_core_lib.data.sellerdb)
        userdb_session = SqlAlchemyDataHandlerRegistry(self.config.core_lib.facebook_core_lib.data.userdb)
        self.details = DetailsDataAccess(userdb_session)
        self.data = DataDataAccess(userdb_session)
        self.details = SellerDetailsDataAccess(sellerdb_session)
        self.data = SellerDataAccess(sellerdb_session)
        jobs_data_handlers = {}
        self.load_jobs(self.config.core_lib.facebook_core_lib.jobs, jobs_data_handlers)
