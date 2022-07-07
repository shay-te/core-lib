from omegaconf import OmegaConf

from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry


def connect_to_mem_db():
    conf = {
        'create_db': True,
        'log_queries': False,
        'session': {'pool_recycle': 3600, 'pool_pre_ping': False},
        'url': {'protocol': 'sqlite'},
    }
    return SqlAlchemyConnectionRegistry(OmegaConf.create(conf))
