from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class ReadmeGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = template_content.replace('TemplateCoreLib', f'{snake_to_camel(core_lib_name)}')
        return updated_file.replace('template_core_lib', f'{core_lib_name}')

    def get_template_file(self, yaml_data: dict) -> str:
        return 'core_lib_generator/template_core_lib/README.md'
