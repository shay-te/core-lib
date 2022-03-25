from omegaconf import OmegaConf

from core_lib_generator.file_generators.template_generator import TemplateGenerator


class ConfigGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        config = OmegaConf.create({'core_lib': {core_lib_name: yaml_data}})
        return template_content.replace('template', OmegaConf.to_yaml(config))

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/template_core_lib/config/template_core_lib.yaml'
