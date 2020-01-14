import enum

from sqlalchemy import Column, Date, Integer, VARCHAR
from core_lib.data_layers.data.db.base import Base
from core_lib.data_layers.data.db.enums.int_enum import IntEnum
from core_lib.data_layers.data.db.mixins.time_stamp_mixin import TimeStampMixin


class User(TimeStampMixin, Base):

    __tablename__ = 'user'

    class Gender(enum.Enum):
        FEMALE = enum.auto()
        MALE = enum.auto()

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(VARCHAR(length=255), nullable=False)
    password = Column(VARCHAR(length=100), nullable=False)
    nick_name = Column(VARCHAR(length=255), nullable=False)
    first_name = Column(VARCHAR(length=255), nullable=False)
    middle_name = Column(VARCHAR(length=255))
    last_name = Column(VARCHAR(length=255))
    email = Column(VARCHAR(length=255), nullable=False)

    birthday = Column(Date, nullable=False)

    gender = Column('gender', IntEnum(Gender))
