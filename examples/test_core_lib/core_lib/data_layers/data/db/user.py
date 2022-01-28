import enum

from sqlalchemy import Column, Date, Integer, VARCHAR
from sqlalchemy.orm import validates

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.time_stamp_mixin import TimeStampMixin
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum
from core_lib.helpers.validation import is_email


class User(TimeStampMixin, Base):

    __tablename__ = 'user'

    class Gender(enum.Enum):
        FEMALE = enum.auto()
        MALE = enum.auto()

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(VARCHAR(length=255), nullable=False)
    username = Column(VARCHAR(length=255), nullable=False)
    password = Column(VARCHAR(length=100), nullable=False)
    nick_name = Column(VARCHAR(length=255), nullable=False)
    first_name = Column(VARCHAR(length=255), nullable=False)
    middle_name = Column(VARCHAR(length=255))
    last_name = Column(VARCHAR(length=255))
    birthday = Column(Date, nullable=False)
    gender = Column('gender', IntEnum(Gender))

    @validates('email')
    def validate_email(self, key, email):
        if not email or not is_email(email):
            raise AssertionError('email must be ser and valid')
        return email
