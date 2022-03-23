import re
from re import split


def snake_to_camel(snake_str) -> str:
    return ''.join(x.title() for x in snake_str.split('_'))


def camel_to_snake(s) -> str:
    return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')


def any_to_camel(string: str) -> str:
    if not _is_camel_case(string):
        return ''.join(a.capitalize() for a in split('([^a-zA-Z0-9])', string) if a.isalnum())
    else:
        return re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), string, 1)  # capitalize first word just in case


def _is_camel_case(string: str) -> bool:
    return string != string.lower() and string != string.upper() and "_" not in string and " " not in string
