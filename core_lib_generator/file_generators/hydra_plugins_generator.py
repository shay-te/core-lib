from omegaconf import OmegaConf

from core_lib.helpers.string import snake_to_camel
from core_lib_generator.file_generators.template_generate import TemplateGenerate


class HydraPluginsGenerateTemplate(TemplateGenerate):
    def generate(self, template_file: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        new_file = template_file.replace('TemplateCoreLibSearchPathPlugin', f'{snake_to_camel(core_lib_name)}SearchPathPlugin')
        new_file = new_file.replace('template_core_lib', core_lib_name)
        return new_file

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/hydra_plugins/template_core_lib.py'
