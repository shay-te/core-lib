import os
import shutil

from core_lib_generator.generator_file_utils import replace_file_strings, replace_file_line
from core_lib_generator.file_generators.template_generate import TemplateGenerate


def add_columns_to_entity(filename: str, columns: dict):
    import_data_types = ['INTEGER']
    id_str = 'id = Column(INTEGER, primary_key=True, nullable=False)'
    columns_str = [id_str.rjust(len(id_str) + 4)]
    for key in columns:
        import_data_types.append(columns[key]['type'])
        column_type = columns[key]['type']
        default = None if not columns[key]['default'] else columns[key]['default']
        columns_str.append(f'{key:>{len(key) + 4}} = Column({column_type}, nullable=False, default={default})')
    replace_file_line(filename, '# template_column', '\n'.join(columns_str))
    imports_to_add = ', '.join(set(import_data_types))
    replace_file_line(filename, '# template_import', f'from sqlalchemy import Column, {imports_to_add}')


class EntityGenerateTemplate(TemplateGenerate):
    def handle(self, template_path: str, yaml_data: dict):
        if not os.path.isfile(template_path):
            if yaml_data['is_soft_delete'] and yaml_data['is_soft_delete_token']:
                shutil.copy(
                    f'template_core_lib/core_lib/data_layers/data/db/entities/template_soft_delete_token.py',
                    template_path,
                )
            elif yaml_data['is_soft_delete'] and not yaml_data['is_soft_delete_token']:
                shutil.copy(
                    f'template_core_lib/core_lib/data_layers/data/db/entities/template_soft_delete.py',
                    template_path,
                )
            else:
                shutil.copy(
                    f'template_core_lib/core_lib/data_layers/data/db/entities/template.py',
                    template_path,
                )
            add_columns_to_entity(template_path, yaml_data['columns'])
            entity_name = yaml_data['name']
            replace_file_strings(template_path, 'template', f'{entity_name.lower()}')
            replace_file_strings(template_path, 'Template', f'{entity_name.title()}')
