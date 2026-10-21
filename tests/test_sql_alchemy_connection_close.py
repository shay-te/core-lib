"""SqlAlchemyConnection rolls back a failed commit and always returns its database connection to the pool."""
import os
import shutil
import tempfile
import unittest

from omegaconf import OmegaConf
from sqlalchemy import Column, Integer, VARCHAR, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base

from core_lib.connection.sql_alchemy_connection import SqlAlchemyConnection
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory

# A base of its own, so this table never joins core-lib's shared Base.metadata.
LocalBase = declarative_base()


class Widget(LocalBase):
    __tablename__ = 'acme_widget'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(50), nullable=False, unique=True)


class TestSqlAlchemyConnectionClose(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        db_file = os.path.relpath(os.path.join(self.folder, 'acme.db'))  # a file: a pooled, real connection
        self.factory = SqlAlchemyConnectionFactory(
            OmegaConf.create({'create_db': False, 'url': {'protocol': 'sqlite', 'file': db_file}})
        )
        LocalBase.metadata.create_all(self.factory.engine)
        with self.factory.get() as session:
            session.add(Widget(name='widget'))
        self.checked_out_baseline = self.factory.engine.pool.checkedout()

    def tearDown(self):
        self.factory.connection.close()
        self.factory.engine.dispose()
        shutil.rmtree(self.folder)

    def _stored_names(self):
        with self.factory.get() as session:
            return sorted(session.scalars(select(Widget.name)).all())

    def test_failed_commit_rolls_back_and_releases_the_connection(self):
        connection = self.factory.get()
        with self.assertRaises(IntegrityError):
            with connection as session:
                session.add(Widget(name='gadget'))
                session.add(Widget(name='widget'))  # duplicate: the commit on exit fails

        self.assertFalse(connection.session.in_transaction())
        self.assertEqual(self.checked_out_baseline, self.factory.engine.pool.checkedout())
        self.assertEqual(['widget'], self._stored_names())

    def test_without_on_exit_the_block_leaves_commit_and_close_to_the_caller(self):
        connection = SqlAlchemyConnection(self.factory.engine, None)

        with connection as session:
            session.add(Widget(name='gadget'))

        self.assertTrue(connection.session.in_transaction())  # nothing committed when the block exited
        self.assertEqual(['widget'], self._stored_names())
        connection.close()
        self.assertEqual(['gadget', 'widget'], self._stored_names())
        self.assertEqual(self.checked_out_baseline, self.factory.engine.pool.checkedout())
