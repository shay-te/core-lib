from core_lib.data_transform.helpers import get_dict_attr
from core_lib_generator.generator_utils.formatting_utils import add_tab_spaces


def is_exists(user_input: str, items: list) -> bool:
    for item in items:
        if item['key'] == user_input:
            return False
    return True


def generate_functions(template_content: str, functions: list):
    func_list = []
    imports = []
    for function in functions:
        func_str_list = []
        name = get_dict_attr(function, 'key')
        return_type = get_dict_attr(function, 'return_type')
        if get_dict_attr(function, 'cache_key'):
            imports.append('from core_lib.cache.cache_decorator import Cache')
            cache_key = get_dict_attr(function, 'cache_key')
            cache_invalidate = get_dict_attr(function, 'cache_invalidate')
            invalidate_str = ', invalidate=True' if cache_invalidate else ''
            func_str_list.append(add_tab_spaces(f'@Cache(\'{cache_key}\'{invalidate_str})', 1))
        if get_dict_attr(function, 'result_to_dict'):
            imports.append('from core_lib.data_transform.result_to_dict import ResultToDict')
            func_str_list.append(add_tab_spaces('@ResultToDict()', 1))
        func_str_list.append(add_tab_spaces(f'def {name}(self) -> {return_type}:', 1))
        func_str_list.append(add_tab_spaces('pass', 2))
        func_list.append('\n'.join(func_str_list))
    updated_file = template_content.replace('# template_functions', '\n\n'.join(func_list))
    updated_file = updated_file.replace('# template_function_imports', '\n'.join(set(imports)))
    return updated_file
