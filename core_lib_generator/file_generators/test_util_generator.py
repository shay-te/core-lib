import os
from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class UtilTestGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        camel_case_name: str = snake_to_camel(core_lib_name)

        import_instance_string: str = f'from {core_lib_name}_instance import {camel_case_name}'
        template_content = template_content.replace('# template core_lib_instance', import_instance_string)

        core_lib_import: str = f'from {os.path.basename(os.getcwd())}.{core_lib_name}.{core_lib_name}.{core_lib_name} import {camel_case_name}'
        template_content = template_content.replace('# template_core_lib_import', core_lib_import)

        template_class: str = f'{camel_case_name}Instance'
        template_content = template_content.replace('TemplateInstance', template_class)

        return template_content

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/tests/test_data/helpers/util.py'
