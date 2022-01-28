from sqlalchemy import Column, Integer, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class TestInfo(Base):

    __tablename__ = "test_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nick_name = Column(VARCHAR(length=255))
