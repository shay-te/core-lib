from core_lib.data_layers.data_access.data_access import DataAccess


class DemoDataAccess(DataAccess):

    def __init__(self, data_sessions: list):
        DataAccess.__init__(self, data_sessions)

    def get_by_id(self, demo_id: str):
        with self.get_session() as session:
            session.demos.find_one({'demo_id': demo_id})

    def create(self, demo: dict):
        with self.get_session() as session:
            session.insert_one(demo)
