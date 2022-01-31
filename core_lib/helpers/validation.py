import re

from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


#
# primitives
#
def is_bool(st):
    if isinstance(st, str):
        st = str.lower(st)
        if st == "true" or st == "false":
            return True
        else:
            return False
    elif isinstance(st, bool):
        return True
    else:
        return False


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
    return isinstance(int_value, enum)
