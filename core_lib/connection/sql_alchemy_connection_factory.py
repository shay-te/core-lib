from omegaconf import DictConfig
from sqlalchemy.orm import sessionmaker

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.sql_alchemy_connection import SqlAlchemyConnection
from core_lib.data_layers.data.data_helpers import build_url
from sqlalchemy import create_engine, engine
from core_lib.data_layers.data.db.sqlalchemy.base import Base

UNSUPPORTED_DB_POOL = ['sqlite', 'firebird', 'sybase', 'ibm_db_sa', 'redshift']

class SqlAlchemyConnectionFactory(ConnectionFactory):
    def __init__(self, config: DictConfig):
        """
        Initialize the connection factory with a SQLAlchemy engine, persistent connection, and reusable session factory.
        
        If `create_db` is truthy in config, creates all database tables via SQLAlchemy metadata.
        
        Parameters:
            config (DictConfig): Configuration object containing database URL, connection parameters, and optional `create_db` flag
        """
        self.session_to_count = {}
        self._engine = self._create_engine(config)
        self._connection = self._engine.connect()
        # Build the sessionmaker once per engine and reuse it. sessionmaker
        # is intentionally meant to be long-lived; rebuilding it per
        # SqlAlchemyConnection (the old behavior) wasted work on every
        # .get() and prevented SQLAlchemy from caching against the factory.
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

        if config.get('create_db', True):
            Base.metadata.create_all(self._engine)

    @property
    def engine(self) -> engine:
        return self._engine

    @property
    def connection(self):
        """
        Provide the factory's persistent database connection.
        
        Returns:
        	connection: The SQLAlchemy connection object managed by this factory.
        """
        return self._connection

    def get(self, *args, **kwargs) -> SqlAlchemyConnection:
        """
        Create a new database session.
        
        Returns:
        	SqlAlchemyConnection: A new instance for database operations.
        """
        return SqlAlchemyConnection(self._session_factory, self._on_db_session_exit)

    def _on_db_session_exit(self, db_session: SqlAlchemyConnection):
        """
        Close the database session when its lifecycle ends.
        """
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
