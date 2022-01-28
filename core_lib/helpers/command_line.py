import string

from core_lib.helpers.validation import is_int


def _to_safe_file_name(inputFilename: str):
    safechars = string.ascii_letters + "_"
    try:
        return ''.join(filter(lambda c: c in safechars, inputFilename.replace('-', '_')))
    except:
        return None


def input_file_name(message: str):
    file_name = None
    while not file_name:
        file_name = input('{}: '.format(message))
        file_name = _to_safe_file_name(file_name)
    return file_name


def input_string(message: str):
    content = None
    while not content:
        content = input(message)
    return content


def input_yes_no(message: str, default: bool = True):
    input_y_n = input('{}, Yes/No (enter for {}): '.format(message, 'Yes' if default else 'No')).strip().lower()
    if input_y_n:
        if input_y_n == 'yes' or input_y_n == 'y':
            return True
        elif input_y_n == 'no' or input_y_n == 'n':
            return False
    return default


def input_options(message, options: list, default: str = None):
    input_option = input('{}, {} (enter for {}):'.format(message, ','.join(options), default)).strip().lower()
    if input_option in options:
        return input_option
    else:
        return default


def input_options_list(message, options: list):
    menu = ''
    print(message)
    for index, option in enumerate(options):
        menu = menu + '{}. {}\n'.format(index, option)
    print(menu)

    option_select = None
    while not option_select or not is_int(option_select) or 1 >= int(option_select) >= len(options):
        print('---')
        option_select = input(option_select)
    return option_select
