from core_lib.helpers.validation import is_int


def check_default(value, default_value):
    if not value and default_value is not None:
        return default_value
    else:
        return value


def input_yes_no(title, default_value: bool) -> bool:
    converted_default_value = 'yes' if default_value else 'no'
    user_input = input(f'{title} (yes/no) [default: {converted_default_value}]: ')
    if not user_input:
        user_input = converted_default_value
    while user_input.lower() not in ['yes', 'no', 'n', 'y']:
        user_input = input(f'{title} (yes/no) [default: {converted_default_value}]: ')
        if not user_input:
            user_input = converted_default_value
    if user_input.lower() in ['yes', 'y']:
        return True
    elif user_input.lower() in ['no', 'n']:
        return False


def input_str(title, default_value=None) -> str:
    user_input = input(f'{title} [default: {default_value}]: ')
    user_input = check_default(user_input, default_value)
    while not str(user_input):
        user_input = input(f'{title} [default: {default_value}]: ')
        user_input = check_default(user_input, default_value)
    return str(user_input)


def input_int(title, default_value=None) -> int:
    user_input = input(f'{title} [default: {default_value}]: ')
    user_input = check_default(user_input, default_value)
    while not is_int(user_input):
        user_input = input(f'{title} [default: {default_value}]: ')
        user_input = check_default(user_input, default_value)
    return int(user_input)


def input_enum(enum_class, title) -> int:
    enum_values = set()
    for item in enum_class:
        enum_values.add(item.value)
        print(f'{item.value}-{item.name}')
    user_input = input(f'From the following list, select the relevant number {title}: ')
    while not check_enum(user_input, enum_values):
        user_input = input(f'From the following list, select the relevant number {title}: ')
    return int(user_input)


def check_enum(value, enum_values) -> bool:
    if not is_int(value):
        return False
    elif int(value) not in enum_values:
        return False
    else:
        return True


def input_list(list_value, title):
    [print(f'{list_value.index(i) + 1}-{i}') for i in list_value]
    user_input = input(f'From the following list, select the relevant number {title}: ')
    while not check_list(user_input, list_value):
        user_input = input(f'From the following list, select the relevant number {title}: ')
    return list_value[int(user_input) - 1]


def check_list(value, list_value) -> bool:
    if not is_int(value):
        return False
    elif int(value) > len(list_value) or int(value) <= 0:
        return False
    else:
        return True
