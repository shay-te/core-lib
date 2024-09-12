import os
from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class CoreLibInstanceGenerate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        camel_case_class: str = snake_to_camel(core_lib_name)

        core_lib_import = f'from {os.path.basename(os.getcwd())}.{core_lib_name}.{core_lib_name}.{core_lib_name} import {camel_case_class}'
        template_content = template_content.replace('# template_core_lib_import', core_lib_import)

        template_content = template_content.replace('TemplateCoreLibInstance', f'{camel_case_class}Instance')

        template_content = template_content.replace('Template', f'{camel_case_class}')

        return template_content

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/template_core_lib_instance.py'
