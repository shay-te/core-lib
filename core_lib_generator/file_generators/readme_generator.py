from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class ReadmeGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = template_content.replace('TemplateCoreLib', f'{snake_to_camel(core_lib_name)}')
        updated_file = updated_file.replace('template_core_lib', f'{core_lib_name}')
        return _add_function_calls(updated_file, yaml_data, core_lib_name)

    def get_template_file(self, yaml_data: dict) -> str:
        return 'core_lib_generator/template_core_lib/README.md'


def _add_function_calls(file_content: str, yaml_data: dict, core_lib_name: str):
    updated_file = file_content
    func_call_list = []
    if yaml_data:
        for data_access in yaml_data:
            db_conn = data_access['db_connection']
            db_entity = data_access['entity']
            func_call_list.append(f'{core_lib_name}.{db_conn}_{db_entity}.your_function()')
        updated_file = updated_file.replace('# function_call', '\n'.join(func_call_list))
    else:
        updated_file = updated_file.replace('# function_call', '')
    return updated_file
