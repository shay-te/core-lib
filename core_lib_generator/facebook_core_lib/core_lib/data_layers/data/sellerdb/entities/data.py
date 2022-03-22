from sqlalchemy import Column, VARCHAR, INTEGER

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class Data(Base):
    __tablename__ = 'data'

    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(VARCHAR, nullable=False, default=None)
    password = Column(VARCHAR, nullable=False, default=None)
