# template_import

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin


class Template(Base, SoftDeleteMixin):
    __tablename__ = 'template'

    # template_column
