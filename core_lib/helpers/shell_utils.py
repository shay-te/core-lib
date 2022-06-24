import enum
from typing import Union, Callable, Awaitable

from pytimeparse import parse

from core_lib.helpers.validation import is_int, is_email, is_url, is_float


def input_yes_no(title: str, default_value: bool = None) -> bool:
    converted_default_value = _convert_default_yes_no(default_value)
    result = None
    while result is None:
        user_input = _input(f'{title} (yes/no) {_print_default(converted_default_value)}: ')
        user_input = _get_value(user_input, converted_default_value)
        if user_input in ['yes', 'y', 'no', 'n']:
            result = _check_yes_no(user_input)
    return result


def input_str(
        title: str,
        default_value: str = None,
        allow_empty: bool = False,
        validate_value_callback: Callable[[dict], Awaitable[dict]] = None,
        title_validate_value_fail: str = 'Result value invalid',
        allow_none: bool = False
) -> str:
    result = None
    is_result_valid = True
    while result is None:
        new_title = title if is_result_valid else title_validate_value_fail
        user_input = _input(f'{new_title} {_print_default(default_value, allow_none)}: ')
        user_input = _get_value(user_input, default_value)
        if allow_none and str(user_input) == '':
            break
        if allow_empty and str(user_input) == "''":
            result = str(user_input)
        if str(user_input) and user_input is not None:
            if validate_value_callback and not validate_value_callback(user_input):
                result = None
                is_result_valid = False
            else:
                result = str(user_input)
                is_result_valid = True
    return result


def input_int(title: str, default_value: int = None, allow_none: bool = False) -> int:
    result = None
    while result is None:
        user_input = _input(f'{title} {_print_default(default_value, allow_none)}: ')
        user_input = _get_value(user_input, default_value)
        if is_int(user_input):
            result = int(user_input)
        if allow_none and result is None:
            break
    return result


def input_bool(title: str, default_value: str = None, allow_none: bool = False) -> bool:
    result = None
    while result is None:
        user_input = _input(f'{title} {_print_default(default_value, allow_none)}: ')
        user_input = _get_value(user_input, default_value)
        if user_input.lower() in ['true', 'false', '0', '1']:
            result = True if user_input.lower in ['true', '1'] else False
        if allow_none and result is None:
            break
    return result


def input_timeframe(title: str, default_value: str = None, allow_empty: bool = False) -> str:
    result = None
    while result is None:
        user_input = _input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if user_input in ['boot', 'startup']:
            user_input = '0s'
        if allow_empty and str(user_input) == '':
            result = str(user_input)
        if parse(user_input) is not None:
            result = str(user_input)
    return result


def input_enum(
        enum_class: enum,
        title: str,
        default_value: int = None,
) -> int:
    enum_values = set()
    for item in enum_class:
        enum_values.add(item.value)
        print(f'{item.value}-{item.name}')
    result = None
    while result is None:
        user_input = _input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if is_int(user_input) and int(user_input) in enum_values:
            result = int(user_input)
    return result


def input_list(
        list_value: list,
        title: str,
        default_value: int = None,
        validate_value_callback: Callable[[dict], Awaitable[dict]] = None,
        title_validate_value_fail: str = 'Value already present',
):
    [print(f'{list_value.index(i) + 1}-{i}') for i in list_value]
    result = None
    is_result_valid = True
    while result is None:
        new_title = title if is_result_valid else title_validate_value_fail
        user_input = _input(f'{new_title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if is_int(user_input) and len(list_value) >= int(user_input) > 0:
            if validate_value_callback and not validate_value_callback(list_value[int(user_input) - 1]):
                result = None
                is_result_valid = False
            else:
                result = int(user_input) - 1
                is_result_valid = True
    return result


def input_email(title: str, default_value: str = None) -> str:
    result = None
    while result is None:
        user_input = _input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if is_email(user_input):
            result = user_input
    return result


def input_url(title: str, default_value: str = None, allow_empty: bool = False) -> str:
    result = None
    while result is None:
        user_input = _input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if allow_empty and str(user_input) == '':
            result = str(user_input)
        if is_url(user_input):
            result = user_input
    return result


def _input(print_str: str) -> str:
    user_input = input(print_str)
    return user_input.strip()


def _get_value(value, default_value=None):
    if not value and default_value is not None:
        return default_value
    else:
        return value


def _print_default(default_value, allow_none: bool = False) -> str:
    if default_value is not None:
        return f'[default: {default_value}]'
    elif default_value is None and allow_none:
        return '[None]'
    else:
        return '[Mandatory Input]'


def _convert_default_yes_no(default_value: bool):
    if default_value is not None:
        return 'yes' if default_value else 'no'


def _check_yes_no(value) -> bool:
    if value.lower() in ['yes', 'y']:
        return True
    elif value.lower() in ['no', 'n']:
        return False
