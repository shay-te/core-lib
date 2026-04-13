import re
from contextlib import suppress
from typing import Callable, Optional, TypeVar


ParsedValue = TypeVar("ParsedValue")


#
# primitives
#
def is_bool(val) -> bool:
    if isinstance(val, str):
        return val.lower() in ('true', 'false')
    return isinstance(val, bool)


def is_float(val) -> bool:
    if val is None:
        return False
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


def is_int(val) -> bool:
    if val is None:
        return False
    try:
        int(val)
        return True
    except (ValueError, TypeError, OverflowError):
        return False


#
# complex
#
'''
^                    # Start of string
(?!\.)               # Reject if starts with a dot
(?!.*\.\.)           # Reject if contains consecutive dots
[^@\/\\<>[\]\"]+     # Local part: one or more characters except @, /, \, <, >, [, ], and "
@                    # Literal '@' symbol
[\w]                 # Domain: starts with a word character
[\w.-]*              # Followed by zero or more word characters, dots, or hyphens
\.                   # Dot before TLD
[A-Za-z]{2,}         # TLD: 2 or more alphabetic characters (up to 10 not explicitly enforced)
$                    # End of string
'''
EMAIL_CHECK_REGEX = re.compile(r"^(?!\.)(?!.*\.\.)[^@\/\\<>[\]\"]+@[\w][\w.-]*\.[A-Za-z]{2,}$")

URL_CHECK_REGEX = re.compile(
    r'^(http)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE,
)


def is_email(email: Optional[str]) -> bool:
    if not email:
        return False
    return bool(EMAIL_CHECK_REGEX.fullmatch(email))


def is_int_enum(int_value: Optional[int], enum: object) -> bool:
    with suppress(Exception):
        enum(int_value)
        return True
    return False


def parse_comma_separated_list(
        value,
        value_parser: Optional[Callable[[str], ParsedValue]] = None,
) -> list:
    if value is None or value == "":
        return []

    parser = value_parser or (lambda item: item)
    items = value.split(",") if isinstance(value, str) else value

    result = []
    for item in items:
        cleaned_item = item.strip() if isinstance(item, str) else item
        if cleaned_item == "":
            continue
        result.append(parser(cleaned_item))
    return result


def parse_int_list(value) -> list:
    return parse_comma_separated_list(value, value_parser=int)


def is_url(url: Optional[str]) -> bool:
    if not url:
        return False
    return bool(URL_CHECK_REGEX.match(url))
