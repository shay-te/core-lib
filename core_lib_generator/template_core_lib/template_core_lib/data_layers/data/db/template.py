from sqlalchemy import Column, Integer

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin


class Template(Base, SoftDeleteMixin, SoftDeleteTokenMixin):

    __tablename__ = 'template'

    id = Column(Integer, primary_key=True, nullable=False)
