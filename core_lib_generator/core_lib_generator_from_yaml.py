import os

import hydra
from omegaconf import open_dict

from core_lib.helpers.string import camel_to_snake
from core_lib_generator.file_generators.config_generator import ConfigGenerateTemplate
from core_lib_generator.file_generators.core_lib_class_generator import CoreLibClassGenerateTemplate
from core_lib_generator.file_generators.default_config_generator import DefaultConfigGenerateTemplate
from core_lib_generator.file_generators.dockerignore_generator import DockerIgnoreGenerateTemplate
from core_lib_generator.file_generators.gitignore_generator import GitIgnoreGenerateTemplate
from core_lib_generator.file_generators.hydra_plugins_generator import HydraPluginsGenerateTemplate
from core_lib_generator.file_generators.data_access_generator import DataAccessGenerateTemplate
from core_lib_generator.file_generators.entity_generator import EntityGenerateTemplate
from core_lib_generator.file_generators.jobs_generator import JobsGenerateTemplate
from core_lib_generator.file_generators.manifest_generator import ManifestGenerateTemplate
from core_lib_generator.file_generators.readme_generator import ReadmeGenerateTemplate
from core_lib_generator.file_generators.requirements_generator import RequirementsGenerateTemplate

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize()


class CoreLibGenerator:
    def __init__(self, path_to_config: str):
        config = hydra.compose(path_to_config)
        self.core_lib_name = next(iter(config))
        self.snake_core_lib_name = camel_to_snake(self.core_lib_name)
        self.core_lib_config = config[self.core_lib_name].config

        self.core_lib_entities = {}
        self.core_lib_data_access = {}
        self.core_lib_jobs = {}
        self.core_lib_cache = {}

        if 'data' in config[self.core_lib_name].data_layers:
            self.core_lib_entities = config[self.core_lib_name].data_layers.data
            if 'data_access' in config[self.core_lib_name].data_layers:
                self.core_lib_data_access = config[self.core_lib_name].data_layers.data_access
        if 'jobs' in self.core_lib_config:
            self.core_lib_jobs = self.core_lib_config.jobs
        if 'cache' in self.core_lib_config:
            self.core_lib_cache = self.core_lib_config.cache

        if 'data' in self.core_lib_config:
            for conn_name in self.core_lib_config.data:
                with open_dict(self.core_lib_config.data):
                    if self.core_lib_config.data[conn_name].get('log_queries') is None:
                        self.core_lib_config.data[conn_name].setdefault('log_queries', False)
                    if self.core_lib_config.data[conn_name].get('create_db') is None:
                        self.core_lib_config.data[conn_name].setdefault('create_db', False)
                    if self.core_lib_config.data[conn_name].get('session') is None:
                        self.core_lib_config.data[conn_name].setdefault('session', {})
                        self.core_lib_config.data[conn_name]['session'].setdefault('pool_recycle', 3200)
                        self.core_lib_config.data[conn_name]['session'].setdefault('pool_pre_ping', False)

    def _generate_template(self, file_path: str, yaml_data: dict, template_generate, file_name: str = None):
        template_generator = template_generate()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.isfile(f'{os.path.dirname(file_path)}/__init__.py') and 'hydra_plugins' not in os.path.dirname(
            file_path
        ):
            open(f'{os.path.dirname(file_path)}/__init__.py', 'w').close()
        os.makedirs(f'{self.snake_core_lib_name}/hydra_plugins/conf', exist_ok=True)
        open(f'{self.snake_core_lib_name}/hydra_plugins/conf/__init__.py', 'w').close()
        with open(template_generator.get_template_file(yaml_data), 'r') as template_file:
            new_file = template_generator.generate(template_file.read(), yaml_data, self.snake_core_lib_name, file_name)
        with open(file_path, 'w') as file:
            file.write(new_file)

    def generate_data_access(self):
        if self.core_lib_data_access:
            for da_name in self.core_lib_data_access:
                self._generate_template(
                    f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/data_layers/data_access/{camel_to_snake(da_name)}.py',
                    self.core_lib_data_access[da_name],
                    DataAccessGenerateTemplate,
                    da_name,
                )

    def generate_entities(self):
        if self.core_lib_entities:
            for db_conn_name in self.core_lib_entities:
                for entity_name in self.core_lib_entities[db_conn_name]:
                    if entity_name == 'migrate':
                        continue
                    self._generate_template(
                        f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/data_layers/data/{db_conn_name}/entities/{entity_name.lower()}.py',
                        self.core_lib_entities[db_conn_name][entity_name],
                        EntityGenerateTemplate,
                        entity_name,
                    )

    def generate_jobs(self):
        if self.core_lib_jobs:
            for name in self.core_lib_jobs:
                self._generate_template(
                    f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/jobs/{name}.py',
                    self.core_lib_jobs[name],
                    JobsGenerateTemplate,
                )

    def generate_core_lib_class(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/{self.snake_core_lib_name}.py',
            {
                'data_access': self.core_lib_data_access,
                'jobs': self.core_lib_jobs,
                'cache': self.core_lib_cache,
            },
            CoreLibClassGenerateTemplate,
        )

    def generate_config(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/config/{self.snake_core_lib_name}.yaml',
            self.core_lib_config,
            ConfigGenerateTemplate,
        )

    def generate_hydra_plugins(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/hydra_plugins/{self.snake_core_lib_name}.py', {}, HydraPluginsGenerateTemplate
        )

    def generate_git_ignore(self):
        self._generate_template(f'{self.snake_core_lib_name}/.gitignore', {}, GitIgnoreGenerateTemplate)

    def generate_docker_ignore(self):
        self._generate_template(f'{self.snake_core_lib_name}/.dockerignore', {}, DockerIgnoreGenerateTemplate)

    def generate_readme(self):
        self._generate_template(f'{self.snake_core_lib_name}/README.md', {}, ReadmeGenerateTemplate)

    def generate_requirements(self):
        self._generate_template(f'{self.snake_core_lib_name}/requirements.txt', {}, RequirementsGenerateTemplate)

    def generate_default_config(self):
        self._generate_template(f'{self.snake_core_lib_name}/core_lib_config.yaml', {}, DefaultConfigGenerateTemplate)

    def generate_manifest(self):
        self._generate_template(f'{self.snake_core_lib_name}/MANIFEST.in', {}, ManifestGenerateTemplate)


if __name__ == '__main__':
    generator = CoreLibGenerator('TemplateCoreLib.yaml')
    generator.generate_data_access()
    generator.generate_entities()
    generator.generate_jobs()
    generator.generate_core_lib_class()
    generator.generate_config()
    generator.generate_hydra_plugins()
    generator.generate_git_ignore()
    generator.generate_docker_ignore()
    generator.generate_readme()
    generator.generate_requirements()
    generator.generate_default_config()
    generator.generate_manifest()
