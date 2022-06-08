from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.string import any_to_pascal
from core_lib_generator.file_generators.template_generator import TemplateGenerator
from core_lib_generator.generator_utils.formatting_utils import add_tab_spaces
from core_lib_generator.generator_utils.helpers import generate_functions


class DataAccessGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        updated_file = template_content.replace('Template', file_name)
        db_conn = get_dict_attr(yaml_data, 'db_connection')
        entity = get_dict_attr(yaml_data, 'entity')
        updated_file = updated_file.replace(
            '# template_entity_imports',
            f'from {core_lib_name}.data_layers.data.{db_conn}.entities.{entity.lower()} import {any_to_pascal(entity)}',
        )
        updated_file = updated_file.replace('db_entity', any_to_pascal(entity))
        functions = get_dict_attr(yaml_data, 'functions')
        if functions:
            updated_file = generate_functions(updated_file, functions)
        else:
            updated_file = updated_file.replace(
                '# template_functions',
                add_tab_spaces('pass', 1)
            )
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        if 'is_crud_soft_delete_token' in yaml_data:
            return 'core_lib_generator/template_core_lib/template_core_lib/data_layers/data_access/template_crud_soft_delete_token_data_access.py'
        elif 'is_crud_soft_delete' in yaml_data:
            return 'core_lib_generator/template_core_lib/template_core_lib/data_layers/data_access/template_crud_soft_delete_data_access.py'
        elif 'is_crud' in yaml_data:
            return 'core_lib_generator/template_core_lib/template_core_lib/data_layers/data_access/template_crud_data_access.py'
        else:
            return (
                'core_lib_generator/template_core_lib/template_core_lib/data_layers/data_access/template_data_access.py'
            )
