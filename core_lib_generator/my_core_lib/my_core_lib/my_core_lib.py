from omegaconf import DictConfig
from core_lib.core_lib import CoreLib


from my_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from my_core_lib.data_layers.data_access.customer_data_access import CustomerDataAccess
from my_core_lib.data_layers.db.user import User
from my_core_lib.data_layers.db.customer import Customer
# template_job_imports


class MyCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf

        # template_data_handlers
        self.user = UserDataAccess(User, db_data_session)
        self.customer = CustomerDataAccess(Customer, db_data_session)
