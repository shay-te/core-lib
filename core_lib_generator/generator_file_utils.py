from pathlib import Path


from core_lib.helpers.string import snake_to_camel


def _create_data_access_imports(data_access_list: list, core_lib_name: str) -> str:
    da_imports = []
    for da_name in data_access_list:
        da_imports.append(
            f'from {core_lib_name}.{core_lib_name}.data_layers.data_access.{da_name} import {snake_to_camel(da_name)}'
        )
    return '\n'.join(da_imports)


def _create_entity_imports(db_entities_list: list, core_lib_name: str) -> str:
    entity_imports = []
    for entity_name in db_entities_list:
        entity_imports.append(
            f'from {core_lib_name}.{core_lib_name}.data_layers.data.db.{entity_name.lower()} import {entity_name}'
        )
    return '\n'.join(entity_imports)


def _create_job_imports(job_list: list, core_lib_name: str, jobs: dict) -> str:
    job_imports = []
    for job_name in job_list:
        class_name = jobs[job_name]['class_name']
        job_imports.append(f'from {core_lib_name}.{core_lib_name}.jobs.{job_name.lower()} import {class_name}')
    return '\n'.join(job_imports)


def replace_file_strings(filename: str, old_string: str, new_string: str) -> bool:
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            return False

    with open(filename, 'w') as f:
        s = s.replace(old_string, new_string)
        f.write(s)
        return True


def replace_file_line(filename: str, old_line: str, new_line: str):
    with open(filename) as fd:
        path = Path(filename)
        text = path.read_text()
        for line in fd:
            line = line.rstrip()
            if old_line in line:
                text = text.replace(line, new_line)
                path.write_text(text)


def add_imports_to_main_class(import_list: list, template_name: str, core_lib_name: str, data: dict = None):
    import_str = ''
    filename = f'{core_lib_name}/{core_lib_name}/{core_lib_name}.py'
    if 'da' in template_name:
        import_str = _create_data_access_imports(import_list, core_lib_name)
    elif 'entity' in template_name:
        import_str = _create_entity_imports(import_list, core_lib_name)
    elif 'job' in template_name:
        import_str = _create_job_imports(import_list, core_lib_name, data)
    replace_file_line(filename, template_name, import_str)
