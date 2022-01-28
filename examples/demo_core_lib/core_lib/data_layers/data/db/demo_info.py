from sqlalchemy import Column, Integer, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class DemoInfo(Base):

    __tablename__ = "demo_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    demo_info_1 = Column(VARCHAR(length=255))
    demo_info_2 = Column(VARCHAR(length=255))
    demo_info_3 = Column(VARCHAR(length=255))
    demo_info_4 = Column(VARCHAR(length=255))
    demo_info_5 = Column(VARCHAR(length=255))
    demo_info_6 = Column(VARCHAR(length=255))
