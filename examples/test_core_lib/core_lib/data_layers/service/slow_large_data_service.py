from core_lib.data_layers.service.service import Service
from examples.test_core_lib.core_lib.data_layers.data_access.slow_large_data_data_access import SlowLargeDataDataAccess


class SlowLargeDataService(Service):
    def __init__(self, data_access: SlowLargeDataDataAccess):
        self.data_access = data_access

    def get_data(self):
        return self.data_access.get_data()

    def set_data(self, data: str):
        return self.data_access.set_data(data)

    def set_data_local(self, data: str):
        return self.data_access.set_data_local(data)