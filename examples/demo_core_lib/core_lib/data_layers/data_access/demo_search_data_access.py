from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data.handler.object_data_handler_factory import ObjectDataHandlerFactory


class DemoSearchDataAccess(DataAccess):
    def __init__(self, data_session_factory: ObjectDataHandlerFactory):
        self.solr = data_session_factory

    def search(self, demo_info: str):
        with self.solr.get() as session:
            filter_queries = ["demo_info_1:*{}*".format(demo_info), "demo_info_2:*{}*".format(demo_info)]
            query = {
                'fq': filter_queries
            }
            return session.search("*:*", **query)
