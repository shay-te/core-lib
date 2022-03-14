import os
import shutil

import hydra

from core_lib.helpers.string import camel_to_snake

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize()
config = hydra.compose('TemplateCoreLib.yaml')

core_lib_name = next(iter(config))

core_lib_config = config[core_lib_name].config
core_lib_data_access = config[core_lib_name].data_layers.data_access

db_entities_list = list(config[core_lib_name].data_layers.data.keys())
if 'migrate' in db_entities_list:
    db_entities_list.remove('migrate')
data_access_list = list(config[core_lib_name].data_layers.data_access.keys())

if not os.path.isdir(camel_to_snake(core_lib_name)):
    shutil.copytree('template_core_lib', camel_to_snake(core_lib_name), dirs_exist_ok=True)
if not os.path.isdir(f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}'):
    os.rename('my_core_lib/template_core_lib', f'my_core_lib/{camel_to_snake(core_lib_name)}')
[
    shutil.copy(
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data/db/template.py',
        f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data/db/{name.lower()}.py',
    )
    for name in db_entities_list
]
for name in data_access_list:
    print('is_crud' in core_lib_data_access[name])
    if 'is_crud_soft_delete_token' in core_lib_data_access[name]:
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template_crud_soft_delete_token_data_access.py',
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
        )
    elif 'is_crud_soft_delete' in core_lib_data_access[name]:
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template_crud_soft_delete_data_access.py',
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
        )
    elif 'is_crud' in core_lib_data_access[name]:
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template_crud_data_access.py',
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
        )
    else:
        shutil.copy(
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/template_data_access.py',
            f'{camel_to_snake(core_lib_name)}/{camel_to_snake(core_lib_name)}/data_layers/data_access/{name.lower()}.py',
        )
