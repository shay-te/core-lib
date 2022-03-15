import fileinput
import glob
import os
import shutil

import hydra

from core_lib.helpers.string import camel_to_snake, snake_to_camel
from core_lib_generator.generator_file_utils import replace_file_strings, add_columns_to_entity, \
    add_imports_to_main_class, add_data_access_instances

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize()
config = hydra.compose('TemplateCoreLib.yaml')

core_lib_name = next(iter(config))
core_lib_config = config[core_lib_name].config
core_lib_data_access = config[core_lib_name].data_layers.data_access
core_lib_entities = config[core_lib_name].data_layers.data
data_access_list = list(config[core_lib_name].data_layers.data_access.keys())
db_entities_list = list(core_lib_entities.keys())
if 'migrate' in db_entities_list:
    db_entities_list.remove('migrate')


def _create_data_access(file_name: str, data_access_type: str):
    template_class_name = snake_to_camel(data_access_type).replace('Crud', 'CRUD')
    da_file_name = f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{file_name.lower()}.py'
    if not os.path.isfile(da_file_name):
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{data_access_type}.py',
            da_file_name,
        )
        replace_file_strings(
            da_file_name,
            f'{template_class_name}',
            f'{snake_to_camel(file_name)}',
        )


def _clean_template_files(folder_path: str):
    for filename in glob.glob(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/{folder_path}/template*'
    ):
        os.remove(filename)


if not os.path.isdir(camel_to_snake(core_lib_name)):
    shutil.copytree('template_core_lib', camel_to_snake(core_lib_name), dirs_exist_ok=True)

if not os.path.isdir(f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}'):
    os.rename(
        f'{camel_to_snake(core_lib_name)}/template_core_lib',
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}',
    )
    os.rename(
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/template_core_lib.py',
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}.py',
    )
    replace_file_strings(
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}.py',
        'TemplateCoreLib',
        f'{core_lib_name}',
    )

# Create Entities
for name in db_entities_list:
    new_file_name = (
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data/db/{name.lower()}.py'
    )
    if not os.path.isfile(new_file_name):
        if core_lib_entities[name]['is_soft_delete'] and core_lib_entities[name]['is_soft_delete_token']:
            shutil.copy(
                f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data/db/template_soft_delete_token.py',
                new_file_name,
            )
        elif core_lib_entities[name]['is_soft_delete'] and not core_lib_entities[name]['is_soft_delete_token']:
            shutil.copy(
                f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data/db/template_soft_delete.py',
                new_file_name,
            )
        else:
            shutil.copy(
                f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data/db/template.py',
                new_file_name,
            )
        add_columns_to_entity(new_file_name, core_lib_entities[name]['columns'])
        replace_file_strings(new_file_name, 'template', f'{name.lower()}')
        replace_file_strings(new_file_name, 'Template', f'{name.title()}')

# Clean Template files for entities
_clean_template_files('data_layers/data/db')

# Create data access for entities
for name in data_access_list:
    if 'is_crud_soft_delete_token' in core_lib_data_access[name]:
        _create_data_access(name, 'template_crud_soft_delete_token_data_access')
    elif 'is_crud_soft_delete' in core_lib_data_access[name]:
        _create_data_access(name, 'template_crud_soft_delete_data_access')
    elif 'is_crud' in core_lib_data_access[name]:
        _create_data_access(name, 'template_crud_data_access')
    else:
        _create_data_access(name, 'template_data_access')

# Clean Template files for data access
_clean_template_files('data_layers/data_access')

# Create Job
jobs = core_lib_config['jobs']
for name in jobs:
    new_file_name = f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/job/{name.lower()}.py'
    if not os.path.isfile(new_file_name):
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/job/template.py',
            new_file_name,
        )
        replace_file_strings(new_file_name, 'Template', jobs[name]['class_name'])

# Clean Template files for jobs
_clean_template_files('job')

add_imports_to_main_class(data_access_list, '# template_da_imports', core_lib_name)
add_imports_to_main_class(db_entities_list, '# template_entity_imports', core_lib_name)
add_data_access_instances(core_lib_data_access, '# template_da_instances', core_lib_name)
# add_data_handler_instance()
