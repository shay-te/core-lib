from core_lib.data_layers.data_access.sessions.data_session_factory import DataSessionFactory
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
    pass
