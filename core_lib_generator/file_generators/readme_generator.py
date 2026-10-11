from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator
from core_lib_generator.generator_utils.formatting_utils import remove_line
from core_lib_generator.generator_utils.naming_utils import service_attribute_name


class ReadmeGenerateTemplate(TemplateGenerator):
    # `yaml_data` is the list of services: the README calls the CoreLib's public services, never a DataAccess.
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = template_content.replace('TemplateCoreLib', f'{snake_to_camel(core_lib_name)}')
        updated_file = updated_file.replace('template_core_lib', f'{core_lib_name}')
        return _add_function_calls(updated_file, yaml_data, core_lib_name)

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/README.md'


def _add_function_calls(file_content: str, yaml_data: dict, core_lib_name: str):
    updated_file = file_content
    func_call_list = []
    if yaml_data:
        for service in yaml_data:
            functions = get_dict_attr(service, 'functions')
            function_name = get_dict_attr(functions[0], 'key') if functions else 'your_function'
            func_call_list.append(f'{core_lib_name}.{service_attribute_name(service["key"])}.{function_name}()')
        updated_file = updated_file.replace('# function_call', '\n'.join(func_call_list))
    else:
        updated_file = remove_line('# function_call', updated_file)
    return updated_file
