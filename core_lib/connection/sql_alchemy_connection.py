import logging

from types import TracebackType
from typing import Optional, Type

from sqlalchemy.orm import sessionmaker, Session

from core_lib.connection.transactional_connection import TransactionalConnection

logger = logging.getLogger(__name__)


class SqlAlchemyConnection(TransactionalConnection):
    def __init__(self, engine, on_exit):
        self.engine = engine
        self.on_exit = on_exit
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)()

    def open(self) -> Session:
        return self.session

    def flush(self) -> None:
        self.session.flush()  # the SQL is sent: ids are set, a duplicate raises here

    def release(self) -> None:
        # let go of the loaded rows and drop unsent writes, as the end of a block outside a transaction does: a
        # later read goes to the database again, and a row changed in memory afterwards is not saved
        self.session.expunge_all()

    def end(self, exec_type: Optional[Type[BaseException]], exec_value: Optional[BaseException],
            traceback: Optional[TracebackType]) -> None:
        if exec_type or exec_value or traceback:
            logger.error("Error in DB handler", exc_info=(exec_type, exec_value, traceback))
            try:
                self.session.rollback()
            except BaseException:
                self.session.close()  # a failed rollback still releases the connection, and never commits
                raise

        if self.on_exit:
            self.on_exit(self)

    def close(self):
        # finally: a failed commit still closes the session, or its pooled connection leaks
        try:
            self.session.commit()
            self.session.flush()
        finally:
            self.session.close()
