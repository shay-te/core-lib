from core_lib.single_instance import SingleInstance


# this class is the basic data_access class.
# by extending this class you gain
# 1. get_session mechanism
#    This help us to get session generator by the get_session function
#    we can fetch any session(DB, SOLR, S3, etc..) by name/type
#    and also pass parameters to filter a specific connection.
#    see: "from "core_lib.data_layers.data_access.sessions.data_session.DataSession"
# 2. Assure of only single instance of this data access
#
class DataAccess(SingleInstance):

    __instances = []

    def __init__(self, data_sessions: list):
        self.data_sessions = {data_session.get_name(): data_session for data_session in data_sessions}

    def __new__(cls, *args, **kwargs):
        instance = super(SingleInstance, cls).__new__(cls)
        DataAccess.__instances.append(instance)
        return instance

    def get_session(self, name: str, params: dict):
        if not name and self.data_sessions:
            session = next(iter(self.data_sessions.values()))
        else:
            session = self.data_sessions[name].get_session(params)

        return session.get_session(params)
