import os
import shutil

from core_lib_generator.generator_file_utils import replace_file_strings, replace_file_line


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


def generate_entities(entities: dict, core_lib_name):
    entity_list = list(entities.keys())
    if 'migrate' in entity_list:
        entity_list.remove('migrate')
    for name in entity_list:
        new_file_name = f'{core_lib_name}/{core_lib_name}/data_layers/data/db/{name.lower()}.py'
        if not os.path.isfile(new_file_name):
            if entities[name]['is_soft_delete'] and entities[name]['is_soft_delete_token']:
                shutil.copy(
                    f'{core_lib_name}/{core_lib_name}/data_layers/data/db/template_soft_delete_token.py',
                    new_file_name,
                )
            elif entities[name]['is_soft_delete'] and not entities[name]['is_soft_delete_token']:
                shutil.copy(
                    f'{core_lib_name}/{core_lib_name}/data_layers/data/db/template_soft_delete.py',
                    new_file_name,
                )
            else:
                shutil.copy(
                    f'{core_lib_name}/{core_lib_name}/data_layers/data/db/template.py',
                    new_file_name,
                )
            add_columns_to_entity(new_file_name, entities[name]['columns'])
            replace_file_strings(new_file_name, 'template', f'{name.lower()}')
            replace_file_strings(new_file_name, 'Template', f'{name.title()}')
