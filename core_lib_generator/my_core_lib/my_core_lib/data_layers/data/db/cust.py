from sqlalchemy import Column, VARCHAR, INTEGER

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin


class Cust(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'cust'

    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(VARCHAR, nullable=False, default=None)
    password = Column(VARCHAR, nullable=False, default=None)
    contact = Column(INTEGER, nullable=False, default=None)
