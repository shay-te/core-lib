from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.sessions.object_data_session_factory import ObjectDataSessionFactory


class DemoSearchDataAccess(DataAccess):
    def __init__(self, data_session_factory: ObjectDataSessionFactory):
        self.solr = data_session_factory

    def search(self, demo_info: str):
        with self.solr.get_session() as session:
            filter_queries = ["demo_info_1:*{}*".format(demo_info), "demo_info_2:*{}*".format(demo_info)]
            query = {
                'fq': filter_queries
            }
            return session.search("*:*", **query)
