from sqlalchemy import Column, VARCHAR, INTEGER

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin


class User(Base, SoftDeleteMixin):
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True, nullable=False)
    username = Column(VARCHAR, nullable=False, default=None)
    password = Column(VARCHAR, nullable=False, default=None)
