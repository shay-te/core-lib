import glob
import os
import shutil

import hydra
from omegaconf import OmegaConf

from core_lib.helpers.string import camel_to_snake
from core_lib_generator.cache_generator import generate_cache
from core_lib_generator.data_access_generator import generate_data_access, add_data_access_instances
from core_lib_generator.entity_generator import generate_entities
from core_lib_generator.generator_file_utils import (
    replace_file_strings,
    add_imports_to_main_class,
)
from core_lib_generator.jobs_generator import generate_jobs, add_job_instances

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize()
config = hydra.compose('TemplateCoreLib.yaml')

core_lib_name = next(iter(config))
snake_core_lib_name = camel_to_snake(core_lib_name)
core_lib_config = config[core_lib_name].config
core_lib_entities = config[core_lib_name].data_layers.data
db_entities_list = list(core_lib_entities.keys())
if 'migrate' in db_entities_list:
    db_entities_list.remove('migrate')
core_lib_data_access = config[core_lib_name].data_layers.data_access
data_access_list = list(config[core_lib_name].data_layers.data_access.keys())


def _clean_template_files(folder_path: str):
    for filename in glob.glob(f'{snake_core_lib_name}/{snake_core_lib_name}/{folder_path}/template*'):
        os.remove(filename)


if not os.path.isdir(snake_core_lib_name):
    shutil.copytree('template_core_lib', snake_core_lib_name, dirs_exist_ok=True)
    print(f'Creating {snake_core_lib_name} directory')

if not os.path.isdir(f'{snake_core_lib_name}/{snake_core_lib_name}'):
    os.rename(
        f'{snake_core_lib_name}/template_core_lib',
        f'{snake_core_lib_name}/{snake_core_lib_name}',
    )
    with open(f'{snake_core_lib_name}/config/config.yaml', 'w') as conf:
        conf.write(OmegaConf.to_yaml(core_lib_config))
    os.rename(
        f'{snake_core_lib_name}/{snake_core_lib_name}/template_core_lib.py',
        f'{snake_core_lib_name}/{snake_core_lib_name}/{snake_core_lib_name}.py',
    )
    replace_file_strings(
        f'{snake_core_lib_name}/{snake_core_lib_name}/{snake_core_lib_name}.py',
        'TemplateCoreLib',
        f'{core_lib_name}',
    )
    print(f'Renaming files in {snake_core_lib_name} directory')


if db_entities_list:
    generate_entities(core_lib_entities, snake_core_lib_name)
    add_imports_to_main_class(db_entities_list, '# template_entity_imports', snake_core_lib_name)
    _clean_template_files('data_layers/data/db')
    print(f'Creating database entities')

    if data_access_list:
        generate_data_access(core_lib_data_access, snake_core_lib_name)
        add_imports_to_main_class(data_access_list, '# template_da_imports', snake_core_lib_name)
        add_data_access_instances(core_lib_data_access, snake_core_lib_name)
        _clean_template_files('data_layers/data_access')
        print(f'Creating data access for entities')


# Create Job
if 'jobs' in core_lib_config:
    jobs = core_lib_config['jobs']
    generate_jobs(jobs, snake_core_lib_name)
    add_imports_to_main_class(list(jobs.keys()), '# template_job_imports', snake_core_lib_name, jobs)
    add_job_instances(jobs, snake_core_lib_name)
    _clean_template_files('jobs')
    print(f'Creating jobs')

generate_cache(core_lib_config['cache'], snake_core_lib_name)

print(f'\nCreated {core_lib_name}!')
