from core_lib.helpers.validation import is_int


def _check_default(value, default_value):
    if not value and default_value is not None:
        return default_value
    else:
        return value


def _print_default(default_value):
    if default_value is not None:
        return f' [default: {default_value}]'
    else:
        return ' [Mandatory Input]'


def input_yes_no(title, default_value: bool = None) -> bool:
    converted_default_value = 'yes' if default_value else 'no'
    take_input = True
    while take_input:
        user_input = input(f'{title} (yes/no){_print_default(converted_default_value)}: ')
        if not user_input:
            user_input = converted_default_value
        if user_input.lower() in ['yes', 'y']:
            return True
        elif user_input.lower() in ['no', 'n']:
            return False


def input_str(title, default_value=None) -> str:
    take_input = True
    while take_input:
        user_input = input(f'{title}{_print_default(default_value)}: ')
        user_input = _check_default(user_input, default_value)
        if str(user_input):
            return str(user_input)


def input_int(title, default_value=None) -> int:
    take_input = True
    while take_input:
        user_input = input(f'{title}{_print_default(default_value)}: ')
        user_input = _check_default(user_input, default_value)
        if is_int(user_input):
            return int(user_input)


def input_enum(enum_class, title, default_value=None) -> int:
    enum_values = set()
    for item in enum_class:
        enum_values.add(item.value)
        print(f'{item.value}-{item.name}')
    take_input = True
    while take_input:
        user_input = input(f'{title}{_print_default(default_value)}: ')
        user_input = _check_default(user_input, default_value)
        if is_int(user_input) and int(user_input) in enum_values:
            return int(user_input)


def input_list(list_value, title, default_value=None):
    [print(f'{list_value.index(i) + 1}-{i}') for i in list_value]
    take_input = True
    while take_input:
        user_input = input(f'{title}{_print_default(default_value)}: ')
        user_input = _check_default(user_input, default_value)
        if is_int(user_input) and int(user_input) <= len(list_value) or int(user_input) > 0:
            return list_value[int(user_input) - 1]
