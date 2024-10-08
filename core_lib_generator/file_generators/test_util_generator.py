import os
from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class UtilTestGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        camel_case_name: str = snake_to_camel(core_lib_name)

        core_lib_import: str = f'from {core_lib_name}.{core_lib_name} import {camel_case_name}'
        template_content = template_content.replace('# template_core_lib_import', core_lib_import)

        template_content = template_content.replace('TemplateCoreLibClass', camel_case_name)

        template_class: str = f'{camel_case_name}Instance'
        template_content = template_content.replace('TemplateInstance', template_class)

        template_content = template_content.replace(
            '# template_sync_create_core_lib_import',
            f'from {core_lib_name}.tests.test_data.helpers.util import sync_create_start_core_lib'
        )

        return template_content

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/tests/test_data/helpers/util.py'
