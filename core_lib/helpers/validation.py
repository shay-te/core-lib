import re

from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


#
# primitives
#
def is_bool(st):
    st = str.lower(st)
    return st == "true" or st == "false"


def is_float(st):
    try:
        float(st)
        return True
    except ValueError:
        return False


def is_int(s):
    if s is None:
        return False
    try:
        int(s)
        return True
    except ValueError:
        return False


#
# complex
#
def is_email(email: str) -> bool:
    return bool(re.search(r"^[\w\.\+\-]+\@[\w.]+\.[a-z]{2,3}$", email))


def is_int_enum(int_value: int, enum: IntEnum) -> bool:
    return 0 <= int_value.value <= len(enum)
