import re
from contextlib import suppress

from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


#
# primitives
#
def is_bool(val) -> bool:
    if isinstance(val, str):
        st = str.lower(val)
        return True if st == "true" or st == "false" else False
    else:
        return True if isinstance(val, bool) else False


def is_float(val) -> bool:
    if val is None:
        return False
    try:
        float(val)
        return True
    except Exception:
        return False


def is_int(val) -> bool:
    if val is None:
        return False
    try:
        int(val)
        return True
    except Exception:
        return False


#
# complex
#
EMAIL_CHECK_REGEX = r'^\b[\w\D][^<>\[\]]+@[\w.-]+\.[A-Z|a-z]{2,}\b$'
def is_email(email: str) -> bool:
    if email is None:
        return False
    return True if re.fullmatch(EMAIL_CHECK_REGEX, email) else False


def is_int_enum(int_value: int, enum: IntEnum) -> bool:
    with suppress(Exception):
        enum(int_value)
        return True
    return False


def is_url(url: str) -> bool:
    regex = re.compile(
        r'^(http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE,
    )
    return True if re.match(regex, url) is not None else False
