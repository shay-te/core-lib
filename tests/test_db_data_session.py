import os
import shutil
import tempfile
import unittest
from contextlib import suppress

from omegaconf import OmegaConf
from sqlalchemy import Integer, Column, VARCHAR, text
from sqlalchemy.dialects import registry

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data.db.sqlalchemy.base import Base

from tests.test_data.test_utils import connect_to_mem_db

POOL_SESSION = {'pool_size': 3, 'max_overflow': 4}
# SQLAlchemy's SQLite driver registered under a dialect name of its own, as a third-party dialect registers: it
# pools like a server database (which these tests cannot reach) and is not on the factory's no-pool list.
POOLING_DIALECT = 'acme_pooling'


class Test(Base):

    __tablename__ = 'test'

    id = Column(Integer, primary_key=True, nullable=False)
    test_name = Column(VARCHAR(length=255), nullable=False, default="")


class TestDBDataSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_data_session = connect_to_mem_db()

    def test_query(self):
        with self.__class__.db_data_session.get() as session:
            # Add new
            test = Test()
            test.test_name = "test_name"
            session.add(test)
            session.commit()
            session.flush()
            session.close()

        # Update
        with self.__class__.db_data_session.get() as session:
            with suppress(Exception):
                session.add(Test({"test_name": "Test name 11", "new_!": "not existing field"}))

        with self.__class__.db_data_session.get() as session:
            session.query(Test).filter(Test.id == test.id).update({"test_name": "new name2"})

            session.query(Test).all()

    def test_pool_settings_reach_a_pooling_dialect_and_skip_sqlite_with_or_without_its_driver(self):
        folder = tempfile.mkdtemp()
        db_file = os.path.relpath(os.path.join(folder, 'acme.db'))  # a file: SQLAlchemy pools it with a QueuePool
        registry.register(POOLING_DIALECT, 'sqlalchemy.dialects.sqlite.pysqlite', 'SQLiteDialect_pysqlite')
        factories = {}
        try:
            for protocol in (POOLING_DIALECT, 'sqlite', 'sqlite+pysqlite'):
                config = {'create_db': False, 'session': POOL_SESSION, 'url': {'protocol': protocol, 'file': db_file}}
                factories[protocol] = SqlAlchemyConnectionFactory(OmegaConf.create(config))

            self.assertEqual(3, factories[POOLING_DIALECT].engine.pool.size())
            # SQLite is on the no-pool list under any driver, so SQLAlchemy's own default size applies.
            self.assertEqual(5, factories['sqlite'].engine.pool.size())
            self.assertEqual(5, factories['sqlite+pysqlite'].engine.pool.size())
        finally:
            for factory in factories.values():
                factory.connection.close()
                factory.engine.dispose()
            registry.deregister(POOLING_DIALECT)
            shutil.rmtree(folder)

    def test_in_memory_sqlite_named_with_its_driver_ignores_pool_settings(self):
        # An in-memory SQLite pool takes no max_overflow: passing it raised TypeError.
        config = {'create_db': False, 'session': POOL_SESSION, 'url': {'protocol': 'sqlite+pysqlite'}}
        factory = SqlAlchemyConnectionFactory(OmegaConf.create(config))
        try:
            with factory.get() as session:
                self.assertEqual(1, session.execute(text('SELECT 1')).scalar())
        finally:
            factory.connection.close()
            factory.engine.dispose()
