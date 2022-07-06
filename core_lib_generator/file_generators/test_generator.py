from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.string import snake_to_camel, camel_to_snake
from core_lib_generator.file_generators.template_generator import TemplateGenerator
from core_lib_generator.generator_utils.formatting_utils import add_tab_spaces, remove_line


class TestGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = template_content
        camel_core_lib = snake_to_camel(core_lib_name)
        core_lib_import = f'from {core_lib_name}.{core_lib_name} import {camel_core_lib}'
        updated_file = updated_file.replace('# template_core_lib_import', core_lib_import)
        updated_file = updated_file.replace('TemplateCoreLib', camel_core_lib)
        updated_file = updated_file.replace('template_snake_core_lib', core_lib_name)
        if get_dict_attr(yaml_data, 'services'):
            service_imports_list = []
            service_test_functions = []
            for service in get_dict_attr(yaml_data, 'services'):
                test_function = []
                service_name = get_dict_attr(service, 'key')
                snake_service_name = camel_to_snake(service_name)
                service_imports_list.append(f'from {core_lib_name}.data_layers.service.{snake_service_name} import {service_name}')
                test_function.append(add_tab_spaces(f'def test_{snake_service_name}(self):'))
                test_function.append(
                    add_tab_spaces(
                        f'# here you can test the functions in {service_name} service, e.g. self.assertNone(self.{core_lib_name}.{snake_service_name}.your_function(data))',
                        2
                    )
                )
                test_function.append(add_tab_spaces('pass', 2))
                service_test_functions.append('\n'.join(test_function))
            updated_file = updated_file.replace('# template_test_imports', '\n'.join(service_imports_list))
            updated_file = updated_file.replace('# template_test_functions', '\n\n'.join(service_test_functions))
        elif get_dict_attr(yaml_data, 'data_accesses'):
            da_imports_list = []
            da_test_functions = []
            for data_access in get_dict_attr(yaml_data, 'data_accesses'):
                test_function = []
                da_name = get_dict_attr(data_access, 'key')
                snake_da_name = camel_to_snake(da_name)
                da_imports_list.append(f'from {core_lib_name}.data_layers.data_access.{snake_da_name} import {da_name}')
                test_function.append(add_tab_spaces(f'def test_{snake_da_name}(self):'))
                test_function.append(
                    add_tab_spaces(
                        f'# here you can test the functions in {da_name} data access, e.g. self.assertNone(self.{core_lib_name}.{snake_da_name}.your_function(data))',
                        2
                    )
                )
                test_function.append(add_tab_spaces('pass', 2))
                da_test_functions.append('\n'.join(test_function))
            updated_file = updated_file.replace('# template_test_imports', '\n'.join(da_imports_list))
            updated_file = updated_file.replace('# template_test_functions', '\n\n'.join(da_test_functions))
        else:
            updated_file = remove_line('# template_test_imports', updated_file)
            test_instructions = f'# You can write tests for your Service functions or your DataAccess functions below, by using the Core-Lib instace created above'
            updated_file = updated_file.replace('# template_test_functions', add_tab_spaces(test_instructions))
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/tests/test_template.py'