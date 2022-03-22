from core_lib_generator.file_generators.template_generate import TemplateGenerate


class JobsGenerateTemplate(TemplateGenerate):
    def generate(self, template_file: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        job_class = yaml_data['handler']['_target_'].split('.')[-1]
        return template_file.replace('Template', job_class)

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/core_lib/jobs/template.py'

