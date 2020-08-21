from core_lib.data_layers.service.service import Service
from examples.demo_core_lib.core_lib.data_layers.data_access.demo_search_data_access import DemoSearchDataAccess


class DemoSearchService(Service):

    def __init__(self, search_data_access: DemoSearchDataAccess):
        self.search_data_access = search_data_access

    def search(self, demo_info: str):
        return self.search_data_access.search(demo_info)
