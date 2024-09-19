import os
from core_lib.helpers.string import snake_to_camel
from core_lib_generator.core_lib_config_generate_yaml import ServerType
from core_lib_generator.file_generators.template_generator import TemplateGenerator



class CoreLibInstanceGenerate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        camel_case_class: str = snake_to_camel(core_lib_name)

        if yaml_data.get('server_type'):
            if yaml_data['server_type'] == ServerType.NOSERVER:
                template_content = template_content.replace('# web_helper_template', '')
            elif yaml_data['server_type'] == ServerType.FLASK:
                template_content = template_content.replace('# web_helper_template', 'WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)')
            elif yaml_data['server_type'] == ServerType.DJANGO:
                template_content = template_content.replace('# web_helper_template', 'WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)')
        else:
            template_content = template_content.replace('# web_helper_template', '')

        core_lib_import = f'from {os.path.basename(os.getcwd())}.{core_lib_name}.{core_lib_name}.{core_lib_name} import {camel_case_class}'
        template_content = template_content.replace('# template_core_lib_import', core_lib_import)

        template_content = template_content.replace('TemplateCoreLibInstance', f'{camel_case_class}Instance')

        template_content = template_content.replace('TemplateCoreLibClass', f'{camel_case_class}')

        return template_content

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/template_core_lib_instance.py'
