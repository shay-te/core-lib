from typing import Callable, Awaitable

from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.shell_utils import input_str, input_yes_no
from core_lib_generator.generator_utils.formatting_utils import add_tab_spaces, remove_line


def is_exists(user_input: str, items: list) -> bool:
    for item in items:
        if item['key'] == user_input:
            return False
    return True


def generate_functions(template_content: str, functions: list) -> str:
    func_list = []
    imports = []
    for function in functions:
        func_str_list = []
        name = get_dict_attr(function, 'key')
        if get_dict_attr(function, 'cache_key'):
            imports.append('from core_lib.cache.cache_decorator import Cache')
            cache_key = get_dict_attr(function, 'cache_key')
            cache_invalidate = get_dict_attr(function, 'cache_invalidate')
            invalidate_str = ', invalidate=True' if cache_invalidate else ''
            func_str_list.append(add_tab_spaces(f'@Cache({cache_key.upper()}{invalidate_str})', 1))
        if get_dict_attr(function, 'result_to_dict'):
            imports.append('from core_lib.data_transform.result_to_dict import ResultToDict')
            func_str_list.append(add_tab_spaces('@ResultToDict()', 1))
        func_str_list.append(add_tab_spaces(f'def {name}(self):', 1))
        func_str_list.append(add_tab_spaces('pass', 2))
        func_list.append('\n'.join(func_str_list))
    func_str = '\n\n'.join(func_list)
    updated_file = template_content.replace('# template_functions', f'\n{func_str}')
    if not imports:
        updated_file = remove_line('# template_function_imports', updated_file)
    else:
        updated_file = updated_file.replace('# template_function_imports', '\n'.join(set(imports)))
    return updated_file


def input_function(ask_cache: bool, validate_value_callback: Callable[[dict], Awaitable[dict]] = None) -> dict:
    function_data = {}
    function_name = input_str('What is the name of the function?', None, False, validate_value_callback,
                              'Function with this name already exists')
    result_to_dict = input_yes_no('Do you want the @ResultToDict decorator?', False)
    function_data.update({
        'key': function_name,
        'result_to_dict': result_to_dict,
    })
    if ask_cache:
        if input_yes_no('Do you want to cache the data?', False):
            cache_key = input_str('Enter the name of the cache key (CAPITAL_LETTERS)')
            cache_invalidate = input_yes_no('Do you want to invalidate cache on this function call?', False)
            function_data.update({
                'cache_key': cache_key,
                'cache_invalidate': cache_invalidate,
            })
    return function_data
