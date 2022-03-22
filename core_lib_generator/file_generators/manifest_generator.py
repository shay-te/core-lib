from core_lib_generator.file_generators.template_generate import TemplateGenerate


class ManifestGenerateTemplate(TemplateGenerate):
    def generate(self, template_file: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        return template_file.replace('template_core_lib', core_lib_name)

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/MANIFEST.in'
