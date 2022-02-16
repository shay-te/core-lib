from omegaconf import DictConfig

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.data_handler_registry import DataHandlerRegistry
from core_lib.data_layers.data.handler.sql_alchemy_data_handler import SqlAlchemyDataHandler
from sqlalchemy import create_engine
from core_lib.data_layers.data.db.sqlalchemy.base import Base


class SqlAlchemyDataHandlerRegistry(DataHandlerRegistry):

    def __init__(self, config: DictConfig):
        self.session_to_count = {}
        self._engine = self._create_engine(config)
        self._connection = self._engine.connect()

        if config.get('create_db'):
            Base.metadata.create_all(self._engine)

    @property
    def engine(self):
        return self._engine

    @property
    def connection(self):
        return self._connection

    def get(self, *args, **kwargs) -> SqlAlchemyDataHandler:
        return SqlAlchemyDataHandler(self._engine, self._on_db_session_exit)

    def _on_db_session_exit(self, db_session: SqlAlchemyDataHandler):
        db_session.close()

    def _create_engine(self, config):
        engine = create_engine(build_url(**config.url),
                               pool_recycle=config.session.pool_recycle,
                               echo=config.log_queries)
        return engine
