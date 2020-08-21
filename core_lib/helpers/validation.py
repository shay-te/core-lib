import re

from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


def valid_email(email: str) -> bool:
    return bool(re.search(r"^[\w\.\+\-]+\@[\w.]+\.[a-z]{2,3}$", email))


def valid_int_enum(int_value: int, enum: IntEnum) -> bool:
    return 0 <= int_value.value <= len(enum)
