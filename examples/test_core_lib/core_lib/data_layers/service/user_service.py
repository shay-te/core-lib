from core_lib.data_layers.service.data_transform import ResultToDict
from core_lib.data_layers.service.service import Service
from examples.test_core_lib.core_lib.data_layers.data_access.user_data_access import UserDataAccess


class UserService(Service):
    def __init__(self, data_access: UserDataAccess):
        self.data_access = data_access

    @ResultToDict()
    def create_user(self, user_data):
        return self.data_access.create_user(user_data)

    @ResultToDict()
    def get_user_by_id(self, user_id):
        return self.data_access.get_user_by_id(user_id)

    def update_user(self, user_id: int, update: dict):
        return self.data_access.update_user(user_id, update)

    @ResultToDict()
    def get_or_create_user(self, user_info):
        return self.data_access.get_or_create_user(user_info)
