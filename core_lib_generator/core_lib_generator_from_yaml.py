import os
import shutil

import hydra

from core_lib.helpers.string import camel_to_snake
from core_lib_generator.generator_file_utils import add_imports_to_main_class
from core_lib_generator.file_generators.data_access_generator import DataAccessGenerateTemplate, add_data_access_instances
from core_lib_generator.file_generators.entity_generator import EntityGenerateTemplate
from core_lib_generator.file_generators.jobs_generator import JobsGenerateTemplate

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
            if 'data_access' in config[self.core_lib_name].data_layers:
                self.core_lib_data_access = config[self.core_lib_name].data_layers.data_access
                self.data_access_list = list(config[self.core_lib_name].data_layers.data_access.keys())
        if 'jobs' in self.core_lib_config:
            self.core_lib_jobs = self.core_lib_config.jobs

    def _add_init_file(self):
        folder_iter = os.walk(self.snake_core_lib_name)
        for current_folder, _, _ in folder_iter:
            open(f'{current_folder}/__init__.py', 'w').close()

    def _generate_template(self, file_path: str, yaml_data: dict, template_generate):
        generator = template_generate()
        with open(generator.get_template_file(yaml_data), 'r') as template_file:
            new_file = generator.handle(template_file.read(), yaml_data)
        with open(file_path, 'w') as file:
            file.write(new_file)

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
                self._generate_template(
                    f'{self.snake_core_lib_name}/core_lib/data_layers/data_access/{camel_to_snake(da_name)}.py',
                    self.core_lib_data_access[da_name],
                    DataAccessGenerateTemplate,
                )
            add_imports_to_main_class(self.data_access_list, '# template_da_imports', self.snake_core_lib_name)
            add_data_access_instances(self.core_lib_data_access, self.snake_core_lib_name)
            self._add_init_file()

    def generate_entities(self):
        if self.core_lib_entities:
            for db_conn_name in self.core_lib_entities:
                os.makedirs(
                    f'{self.snake_core_lib_name}/core_lib/data_layers/data/{db_conn_name}/entities', exist_ok=True
                )
                for entity_name in self.core_lib_entities[db_conn_name]:
                    if entity_name == 'migrate':
                        if self.core_lib_entities[db_conn_name][entity_name]:
                            os.makedirs(
                                f'{self.snake_core_lib_name}/core_lib/data_layers/data/{db_conn_name}/migrations/versions',
                                exist_ok=True
                            )
                        continue
                    self._generate_template(
                        f'{self.snake_core_lib_name}/core_lib/data_layers/data/{db_conn_name}/entities/{entity_name.lower()}.py',
                        self.core_lib_entities[db_conn_name][entity_name],
                        EntityGenerateTemplate,
                    )
            # add_imports_to_main_class(self.db_entities_list, '# template_entity_imports', self.snake_core_lib_name)
            self._add_init_file()

    def generate_jobs(self):
        if self.core_lib_jobs:
            for name in self.core_lib_jobs:
                os.makedirs(
                    f'{self.snake_core_lib_name}/core_lib/jobs/', exist_ok=True
                )
                self._generate_template(
                    f'{self.snake_core_lib_name}/core_lib/jobs/{name}.py',
                    self.core_lib_jobs[name],
                    JobsGenerateTemplate,
                )


generate = CoreLibGenerator('TemplateCoreLib.yaml')
generate.generate_core_lib_structure()
generate.generate_data_access()
generate.generate_entities()
generate.generate_jobs()

