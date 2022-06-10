import logging

from sqlalchemy.orm import sessionmaker, Session

from core_lib.connection.connection import Connection

logger = logging.getLogger(__name__)


class SqlAlchemyConnection(Connection):
    def __init__(self, engine, on_exit):
        self.engine = engine
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
