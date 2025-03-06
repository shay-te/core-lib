from omegaconf import DictConfig

from core_lib.connection.connection_registry import ConnectionRegistry
from core_lib.connection.sql_alchemy_connection import SqlAlchemyConnection
from core_lib.data_layers.data.data_helpers import build_url
from sqlalchemy import create_engine, engine
from core_lib.data_layers.data.db.sqlalchemy.base import Base

UNSUPPORTED_DB_POOL = ["sqlite", "firebird", "sybase", "ibm_db_sa", "redshift"]

class SqlAlchemyConnectionRegistry(ConnectionRegistry):
    def __init__(self, config: DictConfig):
        self.session_to_count = {}
        self._engine = self._create_engine(config)
        self._connection = self._engine.connect()

        if config.get('create_db', True):
            Base.metadata.create_all(self._engine)

    @property
    def engine(self) -> engine:
        return self._engine

    @property
    def connection(self):
        return self._connection

    def get(self, *args, **kwargs) -> SqlAlchemyConnection:
        return SqlAlchemyConnection(self._engine, self._on_db_session_exit)

    def _on_db_session_exit(self, db_session: SqlAlchemyConnection):
        db_session.close()

    def _create_engine(self, config) -> engine:
        log_queries = config.get('log_queries', False)
        session = config.get('session', {})
        pool_recycle = session.get('pool_recycle', 3200)
        pool_pre_ping = session.get('pool_pre_ping', False)
        pool_size = session.get('pool_size', 5)
        max_overflow = session.get('max_overflow', 10)

        extra_params = {}
        if config.url.get('protocol') not in UNSUPPORTED_DB_POOL:
            extra_params = {
                'pool_size': pool_size,
                'max_overflow': max_overflow
            }

        return create_engine(
            build_url(**config.url),
            pool_recycle=pool_recycle,
            echo=log_queries,
            pool_pre_ping=pool_pre_ping,
            **extra_params
        )
