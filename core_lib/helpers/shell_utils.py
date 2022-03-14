import enum

from core_lib.helpers.validation import is_int


def _get_value(value, default_value=None):
    if not value and default_value is not None:
        return default_value
    else:
        return value


def _print_default(default_value) -> str:
    if default_value is not None:
        return f'[default: {default_value}]'
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


def input_yes_no(title: str, default_value: bool = None) -> bool:
    converted_default_value = _convert_default_yes_no(default_value)
    result = None
    while result is None:
        user_input = input(f'{title} (yes/no) {_print_default(converted_default_value)}: ')
        user_input = _get_value(user_input, converted_default_value)
        if user_input in ['yes', 'y', 'no', 'n']:
            result = _check_yes_no(user_input)
    return result


def input_str(title: str, default_value: str = None, allow_empty: bool = False) -> str:
    result = None
    while result is None:
        user_input = input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if allow_empty and str(user_input).strip() == '':
            result = str(user_input).strip()
        if str(user_input).strip():
            result = str(user_input).strip().strip('"').strip("'")
    return result


def input_int(title: str, default_value: int = None) -> int:
    result = None
    while result is None:
        user_input = input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if is_int(user_input):
            result = int(user_input)
    return result


def input_bool(title: str, default_value: str = None) -> bool:
    result = None
    while result is None:
        user_input = input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if user_input.lower() in ['true', 'false', '0', '1']:
            if user_input.lower in ['true', '1']:
                result = True
            else:
                result = False
    return result


def input_enum(enum_class: enum, title: str, default_value: int = None) -> int:
    enum_values = set()
    for item in enum_class:
        enum_values.add(item.value)
        print(f'{item.value}-{item.name}')
    result = None
    while result is None:
        user_input = input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if is_int(user_input) and int(user_input) in enum_values:
            result = int(user_input)
    return result


def input_list(list_value: list, title: str, default_value: int = None):
    [print(f'{list_value.index(i) + 1}-{i}') for i in list_value]
    result = None
    while result is None:
        user_input = input(f'{title} {_print_default(default_value)}: ')
        user_input = _get_value(user_input, default_value)
        if is_int(user_input) and int(user_input) <= len(list_value) or int(user_input) > 0:
            result = list_value[int(user_input) - 1]
    return result
