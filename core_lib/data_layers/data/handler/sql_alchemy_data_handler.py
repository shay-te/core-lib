import logging

from sqlalchemy.orm import sessionmaker, Session

from core_lib.data_layers.data.handler.data_handler import DataHandler

logger = logging.getLogger(__name__)


class SqlAlchemyDataHandler(DataHandler):

    def __init__(self, engine, use_parent_instance: bool, on_exit):
        self.engine = engine
        self.use_parent_instance = use_parent_instance
        self.on_exit = on_exit
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)()

    def __enter__(self) -> Session:
        return self.session

    def __exit__(self, exec_type, exec_value, traceback):
        if exec_type or exec_value or traceback:
            logger.error("Error in DB handler", exc_info=(exec_type, exec_value, traceback))
            self.session.rollback()

        if self.on_exit:
            self.on_exit(self)

    def close(self):
        self.session.commit()
        self.session.flush()
        self.session.close()
