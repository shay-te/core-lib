from omegaconf import DictConfig

from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry

from examples.test_core_lib.core_lib.data_layers.data_access.customer_data_access import CustomerDataAccess
from examples.test_core_lib.core_lib.data_layers.data_access.slow_large_data_data_access import SlowLargeDataDataAccess
from examples.test_core_lib.core_lib.data_layers.data_access.test1_data_access import Test1DataAccess
from examples.test_core_lib.core_lib.data_layers.data_access.test2_data_access import Test2DataAccess
from examples.test_core_lib.core_lib.data_layers.data_access.user_data_access import UserDataAccess
from examples.test_core_lib.core_lib.data_layers.service.customer_service import CustomerService
from examples.test_core_lib.core_lib.data_layers.service.slow_large_data_service import SlowLargeDataService
from examples.test_core_lib.core_lib.data_layers.service.test1_service import Test1Service
from examples.test_core_lib.core_lib.data_layers.service.test2_service import Test2Service

from examples.test_core_lib.core_lib.data_layers.service.user_service import UserService


class TestCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf.core_lib
        CoreLib.cache_registry.register("memory_cache", CacheHandlerRam())

        db_data_session = SqlAlchemyConnectionRegistry(self.config.db)

        class Test(object):
            def __init__(self):
                self.test_1 = Test1Service(Test1DataAccess())
                self.test_2 = Test2Service(Test2DataAccess())

        self.test = Test()
        self.user = UserService(UserDataAccess(db_data_session))
        self.customer = CustomerService(CustomerDataAccess(db_data_session))
        self.large_data = SlowLargeDataService(SlowLargeDataDataAccess())
