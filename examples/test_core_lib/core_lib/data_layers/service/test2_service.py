from core_lib.data_layers.service.service import Service
from examples.test_core_lib.core_lib.data_layers.data_access.test2_data_access import Test2DataAccess


class Test2Service(Service):

    def __init__(self, data_access: Test2DataAccess):
        self.data_access = data_access

    def get_value(self):
        return self.data_access.get_value()
