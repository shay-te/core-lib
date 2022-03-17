from omegaconf import DictConfig
from core_lib.core_lib import CoreLib

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry
from my_core_lib.my_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from my_core_lib.my_core_lib.data_layers.data_access.customer_data_access import CustomerDataAccess
from my_core_lib.my_core_lib.data_layers.data.db.user import User
from my_core_lib.my_core_lib.data_layers.data.db.customer import Customer
from my_core_lib.my_core_lib.jobs.my_job import UpdateUser


class MyCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        CoreLib.cache_registry.register(
            'memcached_cache', CacheHandlerMemcached(build_url(host='localhost', port=4444))
        )
        user_db_session = SqlAlchemyDataHandlerRegistry(self.config.data.user_db)
        self.user = UserDataAccess(User, user_db_session)
        self.customer = CustomerDataAccess(Customer, user_db_session)
        self.my_job = UpdateUser()
