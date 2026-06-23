import logging

from sqlalchemy.orm import Session

from core_lib.connection.connection import Connection

logger = logging.getLogger(__name__)


class SqlAlchemyConnection(Connection):
    def __init__(self, session_factory, on_exit):
        # `session_factory` is a SHARED sessionmaker built once on
        # SqlAlchemyConnectionFactory. The previous signature took a raw
        # engine and rebuilt a fresh sessionmaker on every .get() call —
        # wasteful, and it defeated SQLAlchemy's per-factory caches.
        """
        Initialize a SQLAlchemy connection wrapper and establish a session.
        
        Parameters:
            session_factory: A sessionmaker to create sessions from.
            on_exit: A callback invoked when the connection exits.
        """
        self._session_factory = session_factory
        self.on_exit = on_exit
        self.session = session_factory()

    def __enter__(self) -> Session:
        """
        Provide access to the SQLAlchemy session within the context.
        
        Returns:
            Session: The SQLAlchemy session instance.
        """
        return self.session

    def __exit__(self, exec_type, exec_value, traceback):
        """
        Handle session cleanup on context manager exit.
        
        Rolls back the session and logs an error if an exception occurred. Invokes the on_exit callback if configured.
        """
        if exec_type or exec_value or traceback:
            logger.error("Error in DB handler", exc_info=(exec_type, exec_value, traceback))
            self.session.rollback()

        if self.on_exit:
            self.on_exit(self)

    def close(self):
        # flush BEFORE commit so any pending changes are sent to the DB and
        # included in the transaction. flush() AFTER commit() was a no-op
        # (commit already flushed and closed the transaction). Then close
        # to release the connection.
        """
        Finalize pending changes and close the database session.
        """
        self.session.flush()
        self.session.commit()
        self.session.close()
