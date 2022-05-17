from core_lib_generator.file_generators.template_generator import TemplateGenerator


class EnvGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        env_list = []
        for env in yaml_data:
            env_list.append(f'{env}={yaml_data[env]}')
        updated_file = template_content.replace('#template', '\n'.join(env_list))
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        return 'core_lib_generator/template_core_lib/.env'
