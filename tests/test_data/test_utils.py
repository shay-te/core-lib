from omegaconf import OmegaConf

from core_lib.connection.mongodb_connection_registry import MongoDBConnectionRegistry
from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry
from types import SimpleNamespace
import mongomock


def connect_to_mem_db():
    conf = {
        'create_db': True,
        'log_queries': False,
        'session': {'pool_recycle': 3600, 'pool_pre_ping': False},
        'url': {'protocol': 'sqlite'},
    }
    return SqlAlchemyConnectionRegistry(OmegaConf.create(conf))


host = 'server.example.com'
port = 27017


@mongomock.patch(servers=((host, port), ))
def connect_to_mongo():
    conf = {
            'url': {
                'host': host,
                'port': port
            }
    }
    return MongoDBConnectionRegistry(OmegaConf.create(conf))
