from omegaconf import DictConfig

from core_lib.data_layers.data.data_helpers import build_url
from core_lib.data_layers.data.handler.data_handler_factory import DataHandlerRegistry
from core_lib.data_layers.data.handler.sql_alchemy_data_handler import SqlAlchemyDataHandler
from core_lib.helpers.instance_under_stack import InstanceUnderStack
from sqlalchemy import create_engine
from core_lib.data_layers.data.db.sqlalchemy.base import Base


class SqlAlchemyDataHandlerFactory(DataHandlerRegistry):

    def __init__(self, config: DictConfig):
        self.instance_under_path = InstanceUnderStack(stack_start_index=4)
        self.session_to_count = {}
        self._engine = self._create_engine(config)
        if config.create_db:
            Base.metadata.create_all(self._engine)

    def get(self, use_parent_instance=False, *args, **kwargs) -> SqlAlchemyDataHandler:
        if use_parent_instance:
            db_session = self.instance_under_path.get()
            if db_session:
                db_session_count = self.session_to_count[db_session]
                self.session_to_count[db_session] = db_session_count + 1
            else:
                db_session = SqlAlchemyDataHandler(self._engine, use_parent_instance, self._on_db_session_exit)
                self.instance_under_path.store(db_session)
                self.session_to_count[db_session] = 1
            return db_session
        else:
            return SqlAlchemyDataHandler(self._engine, use_parent_instance, self._on_db_session_exit)

    def _on_db_session_exit(self, db_session: SqlAlchemyDataHandler):
        if db_session.use_parent_instance:
            instance_count = self.session_to_count[db_session]
            if instance_count is not None:
                instance_count = instance_count - 1
                self.session_to_count[db_session] = instance_count
                if instance_count == 0:
                    del self.session_to_count[db_session]
                    self.instance_under_path.remove(db_session)
                    db_session.close()
        else:
            db_session.close()

    def _create_engine(self, config):
        engine = create_engine(build_url(**config.url),
                               pool_recycle=config.session.pool_recycle,
                               echo=config.log_queries)
        engine.connect()
        return engine

