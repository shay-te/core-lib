import fileinput
from pathlib import Path

import hydra


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
    id_str = 'id'
    columns_str = [f'{id_str:>{len(id_str) + 4}} = Column(INTEGER, primary_key=True, nullable=False)']
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
            if '#template_column' in line:
                new_line = '\n'.join(columns_str)
                text = text.replace(line, new_line)
                path.write_text(text)
            imports_to_add = ', '.join(set(import_data_types))
            if '#template_import' in line:
                new_line = f'from sqlalchemy import Column, {imports_to_add}'
                text = text.replace(line, new_line)
                path.write_text(text)
