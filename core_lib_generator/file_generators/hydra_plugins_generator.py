from omegaconf import OmegaConf

from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class HydraPluginsGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = template_content.replace('Template', f'{snake_to_camel(core_lib_name)}SearchPathPlugin')
        updated_file = updated_file.replace('template_core_lib', core_lib_name)
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/hydra_plugins/template_core_lib/template_core_lib_searchpath.py'

    def exclude_init_from_dirs(self) -> list:
        return ['hydra_plugins']
