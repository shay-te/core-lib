from core_lib_generator.file_generators.template_generator import TemplateGenerator


class MigrationGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        return template_content

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/template_core_lib/data_layers/data/db/migrations/versions/template_migration.py'
