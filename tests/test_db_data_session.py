import unittest
from contextlib import suppress

from sqlalchemy import create_engine, Integer, Column, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.handler.sql_alchemy_data_handler_factory import SqlAlchemyDataHandlerFactory

# path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_output", "db.db")


class Test(Base):

    __tablename__ = 'test'

    id = Column(Integer, primary_key=True, nullable=False)
    test_name = Column(VARCHAR(length=255), nullable=False, default="")


class TestDBRuleValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", echo=True)
        cls.engine.connect()
        Base.metadata.create_all(cls.engine)
        cls.db_data_session = SqlAlchemyDataHandlerFactory(cls.engine)

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