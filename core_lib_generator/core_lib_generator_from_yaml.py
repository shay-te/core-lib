import fileinput
import glob
import os
import shutil

import hydra

from core_lib.helpers.string import camel_to_snake, snake_to_camel
from core_lib_generator.core_lib_file_updater import replace_file_strings, add_columns_to_entity

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


if not os.path.isdir(camel_to_snake(core_lib_name)):
    shutil.copytree('template_core_lib', camel_to_snake(core_lib_name), dirs_exist_ok=True)
    os.rename(
        f'{camel_to_snake(core_lib_name)}/template_core_lib.py',
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}.py',
    )
    replace_file_strings(
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}.py',
        'TemplateCoreLib',
        f'{core_lib_name}',
    )
if not os.path.isdir(f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}'):
    os.rename(
        f'{camel_to_snake(core_lib_name)}/template_core_lib',
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}',
    )

for name in db_entities_list:
    new_file_name = (
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data/db/{name.lower()}.py'
    )
    shutil.copy(
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data/db/template.py',
        new_file_name,
    )
    add_columns_to_entity(new_file_name, core_lib_entities[name]['columns'])
    replace_file_strings(new_file_name, 'template', f'{name.lower()}')
    replace_file_strings(new_file_name, 'Template', f'{name.title()}')

for name in data_access_list:
    if 'is_crud_soft_delete_token' in core_lib_data_access[name]:
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template_crud_soft_delete_token_data_access.py',
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
        )
        replace_file_strings(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
            'TemplateCRUDSoftDeleteTokenDataAccess',
            f'{snake_to_camel(name)}',
        )
    elif 'is_crud_soft_delete' in core_lib_data_access[name]:
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template_crud_soft_delete_data_access.py',
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
        )
        replace_file_strings(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
            'TemplateCRUDSoftDeleteDataAccess',
            f'{snake_to_camel(name)}',
        )
    elif 'is_crud' in core_lib_data_access[name]:
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template_crud_data_access.py',
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
        )
        replace_file_strings(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
            'TemplateCRUDDataAccess',
            f'{snake_to_camel(name)}',
        )
    else:
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template_data_access.py',
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
        )
        replace_file_strings(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
            'TemplateDataAccess',
            f'{snake_to_camel(name)}',
        )

for filename in glob.glob(
    f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template*'
):
    print(filename)
