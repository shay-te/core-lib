from omegaconf import OmegaConf

from core_lib.connection.mongodb_connection_registry import MongoDBConnectionRegistry
from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry
import mongomock


def connect_to_mem_db():
    conf = {
        'create_db': True,
        'log_queries': False,
        'session': {'pool_recycle': 3600, 'pool_pre_ping': False},
        'url': {'protocol': 'sqlite'},
    }
    return SqlAlchemyConnectionRegistry(OmegaConf.create(conf))


@mongomock.patch(servers=(('server.example.com', 27017), ))
def connect_to_mongo():
    conf = {
            'url': {
                'host': 'server.example.com',
                'port': 27017
            }
    }
    return MongoDBConnectionRegistry(OmegaConf.create(conf))
