from omegaconf import DictConfig, open_dict

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.data_handler_registry import DataHandlerRegistry
from core_lib.data_layers.data.handler.sql_alchemy_data_handler import SqlAlchemyDataHandler
from sqlalchemy import create_engine, engine
from core_lib.data_layers.data.db.sqlalchemy.base import Base


class SqlAlchemyDataHandlerRegistry(DataHandlerRegistry):
    def __init__(self, config: DictConfig):
        self.session_to_count = {}
        with open_dict(config):
            if config.get('log_queries') is None:
                config.setdefault('log_queries', False)
            if config.get('create_db') is None:
                config.setdefault('create_db', True)
            if config.get('session') is None:
                config.setdefault('session', {})
                config['session'].setdefault('pool_recycle', 3200)
                config['session'].setdefault('pool_pre_ping', False)
            if config['session'].get('pool_recycle') is None:
                config['session'].setdefault('pool_recycle', 3200)
            if config['session'].get('pool_pre_ping') is None:
                config['session'].setdefault('pool_pre_ping', False)

        self._engine = self._create_engine(config)
        self._connection = self._engine.connect()

        if config.get('create_db'):
            Base.metadata.create_all(self._engine)

    @property
    def engine(self) -> engine:
        return self._engine

    @property
    def connection(self):
        return self._connection

    def get(self, *args, **kwargs) -> SqlAlchemyDataHandler:
        return SqlAlchemyDataHandler(self._engine, self._on_db_session_exit)

    def _on_db_session_exit(self, db_session: SqlAlchemyDataHandler):
        db_session.close()

    def _create_engine(self, config) -> engine:
        engine = create_engine(
            build_url(**config.url), pool_recycle=config.session.pool_recycle, echo=config.log_queries
        )
        return engine
