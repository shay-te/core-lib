import logging

from sqlalchemy.orm import sessionmaker, Session

from core_lib.connection.transactional_connection import TransactionalConnection

logger = logging.getLogger(__name__)


class SqlAlchemyConnection(TransactionalConnection):
    def __init__(self, engine, on_exit):
        self.engine = engine
        self.on_exit = on_exit
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)()

    def __enter__(self) -> Session:
        return self.session

    def flush(self):
        # send the SQL (ids are set) and let go of the rows, as a block outside a transaction does, so a later
        # read goes to the database again
        self.session.flush()
        self.session.expunge_all()

    def end(self, exec_type, exec_value, traceback):
        if exec_type or exec_value or traceback:
            logger.error("Error in DB handler", exc_info=(exec_type, exec_value, traceback))
            self.session.rollback()

        if self.on_exit:
            self.on_exit(self)

    def close(self):
        # finally: a failed commit still closes the session, or its pooled connection leaks
        try:
            self.session.commit()
            self.session.flush()
        finally:
            self.session.close()
