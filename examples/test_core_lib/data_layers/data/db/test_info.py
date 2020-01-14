from sqlalchemy import Column, String, Integer

from core_lib.data_layers.data.db.base import Base


class TestInfo(Base):

    __tablename__ = "test_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nick_name = Column(String)
