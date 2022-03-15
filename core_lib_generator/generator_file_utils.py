import fileinput
from pathlib import Path

import hydra

from core_lib.helpers.string import camel_to_snake, snake_to_camel


def _create_data_access_imports(data_access_list: list, core_lib_name: str) -> str:
    da_imports = []
    for da_name in data_access_list:
        da_imports.append(
            f'from {camel_to_snake(core_lib_name)}.data_layers.data_access.{da_name} import {snake_to_camel(da_name)}'
        )
    return '\n'.join(da_imports)


def _create_entity_imports(db_entities_list: list, core_lib_name: str) -> str:
    entity_imports = []
    for entity_name in db_entities_list:
        entity_imports.append(
            f'from {camel_to_snake(core_lib_name)}.data_layers.db.{entity_name.lower()} import {entity_name}'
        )
    return '\n'.join(entity_imports)


def replace_file_strings(filename: str, old_string: str, new_string: str) -> bool:
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            return False

    with open(filename, 'w') as f:
        s = s.replace(old_string, new_string)
        f.write(s)
        return True


def add_columns_to_entity(filename: str, columns: dict):
    import_data_types = ['INTEGER']
    id_str = 'id = Column(INTEGER, primary_key=True, nullable=False)'
    columns_str = [id_str.rjust(len(id_str)+4)]
    for key in columns:
        import_data_types.append(columns[key]['type'])
        column_type = columns[key]['type']
        default = None if not columns[key]['default'] else columns[key]['default']
        columns_str.append(f'{key:>{len(key) + 4}} = Column({column_type}, nullable=False, default={default})')
    with open(filename) as fd:
        path = Path(filename)
        text = path.read_text()
        for line in fd:
            line = line.rstrip()
            if '# template_column' in line:
                new_line = '\n'.join(columns_str)
                text = text.replace(line, new_line)
                path.write_text(text)
            imports_to_add = ', '.join(set(import_data_types))
            if '# template_import' in line:
                new_line = f'from sqlalchemy import Column, {imports_to_add}'
                text = text.replace(line, new_line)
                path.write_text(text)


def add_imports_to_main_class(import_list: list, template_name: str, core_lib_name: str):
    import_str = ''
    snake_core_lib_name = camel_to_snake(core_lib_name)
    filename = f'{snake_core_lib_name}/{snake_core_lib_name}/{snake_core_lib_name}.py'
    if 'da' in template_name:
        import_str = _create_data_access_imports(import_list, core_lib_name)
    elif 'entity' in template_name:
        import_str = _create_entity_imports(import_list, core_lib_name)
    with open(filename) as fd:
        path = Path(filename)
        text = path.read_text()
        for line in fd:
            line = line.rstrip()
            if template_name in line:
                new_line = import_str
                text = text.replace(line, new_line)
                path.write_text(text)


def add_data_access_instances(da_data: dict, template_name: str, core_lib_name: str):
    inst_list = []
    snake_core_lib_name = camel_to_snake(core_lib_name)
    filename = f'{snake_core_lib_name}/{snake_core_lib_name}/{snake_core_lib_name}.py'
    for name in da_data:
        entity = da_data[name]['entity']
        inst_str = f'self.{entity.lower()} = {snake_to_camel(name)}({entity.title()}, db_data_session)'
        inst_list.append(
            inst_str.rjust(len(inst_str)+8)
        )
    with open(filename) as fd:
        path = Path(filename)
        text = path.read_text()
        for line in fd:
            line = line.rstrip()
            if template_name in line:
                new_line = '\n'.join(inst_list)
                text = text.replace(line, new_line)
                path.write_text(text)
