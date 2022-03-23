from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generate import TemplateGenerate


class ReadmeGenerateTemplate(TemplateGenerate):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        return template_content.replace('# Template', f'# {snake_to_camel(core_lib_name)}')

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/README.md'
