from core_lib.helpers.string import any_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class DataAccessGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = template_content.replace('Template', file_name)
        db_conn = yaml_data['db_connection']
        entity = yaml_data['entity']
        updated_file = updated_file.replace(
            '# template_entity_imports',
            f'from {core_lib_name}.{core_lib_name}.data_layers.data.{db_conn}.entities.{entity.lower()} import {any_to_camel(entity)}',
        )
        updated_file = updated_file.replace('db_entity', any_to_camel(entity))
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        if 'is_crud_soft_delete_token' in yaml_data:
            return 'template_core_lib/template_core_lib/data_layers/data_access/template_crud_soft_delete_token_data_access.py'
        elif 'is_crud_soft_delete' in yaml_data:
            return (
                'template_core_lib/template_core_lib/data_layers/data_access/template_crud_soft_delete_data_access.py'
            )
        elif 'is_crud' in yaml_data:
            return 'template_core_lib/template_core_lib/data_layers/data_access/template_crud_data_access.py'
        else:
            return 'template_core_lib/template_core_lib/data_layers/data_access/template_data_access.py'
