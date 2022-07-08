from core_lib.data_transform.helpers import get_dict_attr
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class VersionGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        version = get_dict_attr(yaml_data, 'version')
        return template_content.replace('# template_version', f'__version__ = \'{version}\'')

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/template_core_lib/__init__.py'
