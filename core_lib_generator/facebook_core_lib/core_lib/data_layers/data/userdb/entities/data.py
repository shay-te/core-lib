from sqlalchemy import Column, VARCHAR, INTEGER

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin


class Data(Base, SoftDeleteMixin):
    __tablename__ = 'data'

    id = Column(INTEGER, primary_key=True, nullable=False)
    address = Column(VARCHAR, nullable=False, default=None)
    contact = Column(INTEGER, nullable=False, default=None)
