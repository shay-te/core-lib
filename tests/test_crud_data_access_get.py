"""CRUDDataAccess.get uses Session.get: the row by id, a 404 when absent, and no SQLAlchemy legacy-API warning."""
import unittest
import warnings
from http import HTTPStatus

from omegaconf import OmegaConf
from sqlalchemy import Column, Integer, VARCHAR
from sqlalchemy.exc import SADeprecationWarning
from sqlalchemy.orm import declarative_base

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.error_handling.status_code_exception import StatusCodeException

# A base of its own, so this table never joins core-lib's shared Base.metadata.
LocalBase = declarative_base()
ABSENT_WIDGET_ID = 2_000_000_000


class Widget(LocalBase):
    __tablename__ = 'acme_crud_widget'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(50), nullable=False)


class WidgetDataAccess(CRUDDataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory):
        super().__init__(Widget, db)


class TestCRUDDataAccessGet(unittest.TestCase):

    def setUp(self):
        db = SqlAlchemyConnectionFactory(OmegaConf.create({'create_db': False, 'url': {'protocol': 'sqlite'}}))
        LocalBase.metadata.create_all(db.engine)
        self.widget_data_access = WidgetDataAccess(db)

    def test_get_returns_the_row_without_a_legacy_warning(self):
        widget_id = self.widget_data_access.create({Widget.name.key: 'acme-widget'}).id

        with warnings.catch_warnings():
            warnings.simplefilter('error', SADeprecationWarning)
            widget = self.widget_data_access.get(widget_id)

        self.assertEqual(widget_id, widget.id)
        self.assertEqual('acme-widget', widget.name)

    def test_get_absent_id_raises_404(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error', SADeprecationWarning)
            with self.assertRaises(StatusCodeException) as context:
                self.widget_data_access.get(ABSENT_WIDGET_ID)

        self.assertEqual(HTTPStatus.NOT_FOUND, context.exception.status_code)
