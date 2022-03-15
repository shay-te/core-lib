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
    import_data_types = []
    for key in columns:
        import_data_types.append(columns[key]['type'])
        with open(filename, 'a') as fd:
            column_type = columns[key]['type']
            default = None if not columns[key]['default'] else columns[key]['default']
            fd.write(f'\n{key:>{len(key)+4}} = Column({column_type}, nullable=False, default={default})')
    imports_to_add = ', '.join(set(import_data_types))
    with open(filename) as file:
        for line in file:
            line = line.rstrip()
            if 'from sqlalchemy' in line:
                new_line = f'{line}, {imports_to_add}'
                path = Path(filename)
                text = path.read_text()
                text = text.replace(line, new_line)
                path.write_text(text)