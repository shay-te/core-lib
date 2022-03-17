import glob
import os
import shutil

import hydra
from omegaconf import OmegaConf

from core_lib.helpers.string import camel_to_snake
from core_lib_generator.generator_file_utils import add_imports_to_main_class
from core_lib_generator.handlers.data_access_generator import DataAccessGenerateTemplate, add_data_access_instances
from core_lib_generator.handlers.entity_generator import EntityGenerateTemplate
from core_lib_generator.handlers.jobs_generator import add_job_instances, generate_jobs

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize()


class CoreLibGenerator:
    def __init__(self, path_to_config: str):
        config = hydra.compose(path_to_config)

        self.core_lib_name = next(iter(config))
        self.snake_core_lib_name = camel_to_snake(
            self.core_lib_name
        )  # make sure to use _to_safe_file_name() command line helpers
        self.core_lib_config = config[self.core_lib_name].config

        self.core_lib_entities = {}
        self.core_lib_data_access = {}
        self.core_lib_jobs = {}

        if 'data' in config[self.core_lib_name].data_layers:
            self.core_lib_entities = config[self.core_lib_name].data_layers.data
            self.db_entities_list = list(self.core_lib_entities.keys())
            if 'migrate' in self.db_entities_list:
                self.db_entities_list.remove('migrate')
            if 'data_access' in config[self.core_lib_name].data_layers:
                self.core_lib_data_access = config[self.core_lib_name].data_layers.data_access
                self.data_access_list = list(config[self.core_lib_name].data_layers.data_access.keys())
        if 'jobs' in self.core_lib_config:
            self.core_lib_jobs = self.core_lib_config.jobs

    def _add_init_file(self):
        folder_iter = os.walk(self.snake_core_lib_name)
        for current_folder, _, _ in folder_iter:
            open(f'{current_folder}/__init__.py', 'w').close()

    def generate_template(self, template_path: str, yaml_data: dict, template_generate):
        template_generate.handle(self, template_path, yaml_data)

    def generate_core_lib_structure(self):
        os.makedirs(f'{self.snake_core_lib_name}/core_lib/config', exist_ok=True)
        shutil.copy(
            'template_core_lib/core_lib/template_core_lib.py',
            f'{self.snake_core_lib_name}/core_lib/{self.snake_core_lib_name}.py',
        )
        self._add_init_file()

    def generate_data_access(self):
        if self.core_lib_data_access:
            os.makedirs(f'{self.snake_core_lib_name}/core_lib/data_layers/data_access', exist_ok=True)
            for da_name in self.core_lib_data_access:
                self.generate_template(
                    f'{self.snake_core_lib_name}/core_lib/data_layers/data_access/{da_name}.py',
                    self.core_lib_data_access[da_name],
                    DataAccessGenerateTemplate,
                )
            add_imports_to_main_class(self.data_access_list, '# template_da_imports', self.snake_core_lib_name)
            add_data_access_instances(self.core_lib_data_access, self.snake_core_lib_name)
            self._add_init_file()

    def generate_entities(self):
        if self.core_lib_entities:
            os.makedirs(f'{self.snake_core_lib_name}/core_lib/data_layers/data/db/entities', exist_ok=True)
            for entity_name in self.db_entities_list:
                self.generate_template(
                    f'{self.snake_core_lib_name}/core_lib/data_layers/data/db/entities/{entity_name.lower()}.py',
                    self.core_lib_entities[entity_name],
                    EntityGenerateTemplate,
                )
            add_imports_to_main_class(self.db_entities_list, '# template_entity_imports', self.snake_core_lib_name)
            self._add_init_file()

    # def generate_jobs(self):
    #     if 'jobs' in core_lib_config:
    #         jobs = core_lib_config['jobs']
    #         generate_jobs(jobs, snake_core_lib_name)
    #         add_imports_to_main_class(list(jobs.keys()), '# template_job_imports', snake_core_lib_name, jobs)
    #         add_job_instances(jobs, snake_core_lib_name)
    #         print(f'Creating jobs')


generate = CoreLibGenerator('TemplateCoreLib.yaml')
generate.generate_core_lib_structure()
generate.generate_data_access()
generate.generate_entities()
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
