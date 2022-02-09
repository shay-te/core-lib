import re
from contextlib import suppress

from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


#
# primitives
#
def is_bool(st):
    if isinstance(st, str):
        st = str.lower(st)
        return True if st == "true" or st == "false" else False
    else:
        return True if isinstance(st, bool) else False


def is_float(st):
    if st is None:
        return False
    try:
        float(st)
        return True
    except Exception:
        return False


def is_int(s):
    if s is None:
        return False
    try:
        int(s)
        return True
    except Exception:
        return False


#
# complex
#
def is_email(email: str) -> bool:
    regex = r'\b[\w\D][^<>\[\]]+@[\w.-]+\.[A-Z|a-z]{2,}\b'
    if email is None:
        return False
    return True if re.fullmatch(regex, email) else False


def is_int_enum(int_value: int, enum: IntEnum) -> bool:
    with suppress(Exception):
        enum(int_value)
        return True
    return False
