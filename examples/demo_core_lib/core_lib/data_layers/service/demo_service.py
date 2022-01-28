from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib.data_layers.service.service import Service
from examples.demo_core_lib.core_lib.data_layers.data_access.demo_data_access import DemoDataAccess


class DemoService(Service):

    def __init__(self, data_access: DemoDataAccess):
        self.data_access = data_access

    @ResultToDict()
    def create(self, demo_info: dict):
        return self.data_access.create(demo_info)

    def update(self, demo_id: int, demo_info: dict):
        return self.data_access.update(demo_id, demo_info)
