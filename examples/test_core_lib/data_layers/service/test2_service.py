from core_lib.data_layers.service.service import Service
from examples.test_core_lib.data_layers.data_access.test2_data_access import Test2DataAccess


class Test2Service(Service):

    def __init__(self, data_access: Test2DataAccess):
        self.data_access = data_access

    def get_by_id(self, id: int):
        return self.data_access.get_by_id(id)

    def get_by_id_2(self):
        return self.data_access.get_by_id2(id)

