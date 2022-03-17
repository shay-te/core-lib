import glob
import os
import shutil

import hydra
from omegaconf import OmegaConf

from core_lib.helpers.string import camel_to_snake
from core_lib_generator.cache_generator import generate_cache

from core_lib_generator.generator_file_utils import (
    replace_file_strings,
    add_imports_to_main_class,
)
from core_lib_generator.handlers.data_access_generator import DataAccessGenerateTemplate
# from core_lib_generator.handlers.template_generate import TemplateGenerate
from core_lib_generator.handlers.entity_generator import EntityGenerateTemplate
from core_lib_generator.jobs_generator import generate_jobs, add_job_instances


class CoreLibGenerator:
    def __init__(self):
        hydra.core.global_hydra.GlobalHydra.instance().clear()
        hydra.initialize()
        config = hydra.compose('TemplateCoreLib.yaml')

        core_lib_name = next(iter(config))
        self.snake_core_lib_name = camel_to_snake(
            core_lib_name
        )  # make sure to use _to_safe_file_name() command line helpers
        self.core_lib_config = config[core_lib_name].config
        self.core_lib_entities = config[core_lib_name].data_layers.data
        self.db_entities_list = list(self.core_lib_entities.keys())
        if 'migrate' in self.db_entities_list:
            self.db_entities_list.remove('migrate')
        self.core_lib_data_access = config[core_lib_name].data_layers.data_access
        self.data_access_list = list(config[core_lib_name].data_layers.data_access.keys())

    def _clean_template_files(self, folder_path: str):
        for filename in glob.glob(f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/{folder_path}/template*'):
            os.remove(filename)

    def generate_template(self, template_path: str, yaml_data: dict, template_generate):
        template_generate.handle(self, template_path, yaml_data)

    def generate_core_lib_structure(self):
        os.makedirs(f'{self.snake_core_lib_name}/core_lib', exist_ok=True)
        os.makedirs(f'{self.snake_core_lib_name}/config', exist_ok=True)
        shutil.copy(
            'template_core_lib/core_lib/template_core_lib.py',
            f'{self.snake_core_lib_name}/core_lib/{self.snake_core_lib_name}.py',
        )

    def generate_data_access(self):
        if self.core_lib_data_access:
            os.makedirs(f'{self.snake_core_lib_name}/core_lib/data_layers/data_access', exist_ok=True)
            for da_name in self.core_lib_data_access:
                self.generate_template(
                    f'{self.snake_core_lib_name}/core_lib/data_layers/data_access/{da_name}.py',
                    self.core_lib_data_access[da_name],
                    DataAccessGenerateTemplate,
                )

    def generate_entities(self):
        if self.core_lib_entities:
            os.makedirs(f'{self.snake_core_lib_name}/core_lib/data_layers/data/db/entities', exist_ok=True)
            for entity_name in self.db_entities_list:
                self.generate_template(
                    f'{self.snake_core_lib_name}/core_lib/data_layers/data/db/entities/{entity_name.lower()}.py',
                    self.core_lib_entities[entity_name],
                    EntityGenerateTemplate,
                )


generate = CoreLibGenerator()
generate.generate_core_lib_structure()
generate.generate_data_access()
generate.generate_entities()

# if not os.path.isdir(snake_core_lib_name):
#     shutil.copytree('template_core_lib', snake_core_lib_name, dirs_exist_ok=True)
#     print(f'Creating {snake_core_lib_name} directory')
#
# if not os.path.isdir(f'{snake_core_lib_name}/{snake_core_lib_name}'):
#     os.rename(
#         f'{snake_core_lib_name}/template_core_lib',
#         f'{snake_core_lib_name}/{snake_core_lib_name}',
#     )
#     with open(f'{snake_core_lib_name}/config/config.yaml', 'w') as conf:
#         conf.write(OmegaConf.to_yaml(core_lib_config))
#     os.rename(
#         f'{snake_core_lib_name}/{snake_core_lib_name}/template_core_lib.py',
#         f'{snake_core_lib_name}/{snake_core_lib_name}/{snake_core_lib_name}.py',
#     )
#     replace_file_strings(
#         f'{snake_core_lib_name}/{snake_core_lib_name}/{snake_core_lib_name}.py',
#         'TemplateCoreLib',
#         f'{core_lib_name}',
#     )
#     print(f'Renaming files in {snake_core_lib_name} directory')
#
# if db_entities_list:
#     for name in db_entities_list:
#         generate_template()
#     generate_entities(core_lib_entities, snake_core_lib_name)
#     add_imports_to_main_class(db_entities_list, '# template_entity_imports', snake_core_lib_name)
#     _clean_template_files('data_layers/data/db')
#     print(f'Creating database entities')
#
#     if data_access_list:
#         generate_data_access(core_lib_data_access, snake_core_lib_name)
#         add_imports_to_main_class(data_access_list, '# template_da_imports', snake_core_lib_name)
#         add_data_access_instances(core_lib_data_access, snake_core_lib_name)
#         _clean_template_files('data_layers/data_access')
#         print(f'Creating data access for entities')
#
# # Create Job
# if 'jobs' in core_lib_config:
#     jobs = core_lib_config['jobs']
#     generate_jobs(jobs, snake_core_lib_name)
#     add_imports_to_main_class(list(jobs.keys()), '# template_job_imports', snake_core_lib_name, jobs)
#     add_job_instances(jobs, snake_core_lib_name)
#     _clean_template_files('jobs')
#     print(f'Creating jobs')
#
# generate_cache(core_lib_config['cache'], snake_core_lib_name)
# #  take from config
# # config inside the core_lib folder and rename my_core_lib to core_lib
# # add hydra_plugin flder
# # entities folder for entities inside db
# # update db folder structure
# # make entity columns default from yaml file
# # dont copy example_data.yaml, License
# # update manifest .in
# # create readme file with title core lib name
# print(f'\nCreated {core_lib_name}!')
