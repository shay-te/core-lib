import os
import shutil

from core_lib_generator.generator_file_utils import replace_file_strings, replace_file_line
from core_lib_generator.file_generators.template_generate import TemplateGenerate


class EntityGenerateTemplate(TemplateGenerate):
    def handle(self, template_file: str, yaml_data: dict):
        new_file = _add_columns_to_entity(template_file, yaml_data['columns'])
        entity_name = yaml_data['name']
        new_file = new_file.replace('template', f'{entity_name.lower()}')
        new_file = new_file.replace('Template', f'{entity_name.title()}')
        return new_file

    def get_template_data(self, yaml_data: dict) -> str:
        if yaml_data['is_soft_delete'] and yaml_data['is_soft_delete_token']:
            return f'template_core_lib/core_lib/data_layers/data/db/entities/template_soft_delete_token.py'
        elif yaml_data['is_soft_delete'] and not yaml_data['is_soft_delete_token']:
            return f'template_core_lib/core_lib/data_layers/data/db/entities/template_soft_delete.py'
        else:
            return f'template_core_lib/core_lib/data_layers/data/db/entities/template.py'


def _add_columns_to_entity(file: str, columns: dict):
    import_data_types = ['INTEGER']
    id_str = 'id = Column(INTEGER, primary_key=True, nullable=False)'
    columns_str = [id_str]
    for key in columns:
        import_data_types.append(columns[key]['type'])
        column_type = columns[key]['type']
        default = None if not columns[key]['default'] else columns[key]['default']
        columns_str.append(f'{key:>{len(key) + 4}} = Column({column_type}, nullable=False, default={default})')
    file = file.replace('# template_column', '\n'.join(columns_str))
    imports_to_add = ', '.join(set(import_data_types))
    file = file.replace('# template_import', f'from sqlalchemy import Column, {imports_to_add}')
    return file


