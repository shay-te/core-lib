import os
from datetime import datetime

from omegaconf import DictConfig

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
from core_lib_generator.file_generators.license_generator import LicenseGenerateTemplate
from core_lib_generator.file_generators.manifest_generator import ManifestGenerateTemplate
from core_lib_generator.file_generators.readme_generator import ReadmeGenerateTemplate
from core_lib_generator.file_generators.requirements_generator import RequirementsGenerateTemplate
from core_lib_generator.file_generators.setup_generator import SetupGenerateTemplate
from core_lib_generator.file_generators.template_generator import TemplateGenerator
from core_lib_generator.file_generators.version_generator import VersionGenerateTemplate


class CoreLibGenerator:
    def __init__(self, config: DictConfig):
        self.core_lib_name = next(iter(config))
        self.snake_core_lib_name = camel_to_snake(self.core_lib_name)
        self.core_lib_config = config[self.core_lib_name].config

        self.core_lib_entities = {}
        self.core_lib_data_access = {}
        self.core_lib_jobs = {}
        self.core_lib_cache = {}
        self.core_lib_setup = {}

        if 'data' in config[self.core_lib_name].data_layers:
            self.core_lib_entities = config[self.core_lib_name].data_layers.data
            if 'data_access' in config[self.core_lib_name].data_layers:
                self.core_lib_data_access = config[self.core_lib_name].data_layers.data_access
        if 'jobs' in self.core_lib_config:
            self.core_lib_jobs = self.core_lib_config.jobs
        if 'cache' in self.core_lib_config:
            self.core_lib_cache = self.core_lib_config.cache
        if 'setup' in config[self.core_lib_name]:
            self.core_lib_setup = config[self.core_lib_name].setup

    def _generate_template(
            self, file_path: str, yaml_data: dict, template_generator: TemplateGenerator, file_name: str = None
    ):
        file_dir_path = os.path.dirname(file_path)
        os.makedirs(file_dir_path, exist_ok=True)
        excluded_init_dirs = template_generator.exclude_init_from_dirs()
        dir_names = file_dir_path.split('/')
        init_path = ''
        for filename in dir_names:
            init_path = os.path.join(init_path, filename)
            init_file_path = f'{init_path}/__init__.py'
            if not os.path.isfile(init_file_path) and filename not in excluded_init_dirs:
                open(init_file_path, 'w').close()
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
                    DataAccessGenerateTemplate(),
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
                        EntityGenerateTemplate(),
                        entity_name,
                    )

    def generate_jobs(self):
        if self.core_lib_jobs:
            for name in self.core_lib_jobs:
                self._generate_template(
                    f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/jobs/{name}.py',
                    self.core_lib_jobs[name],
                    JobsGenerateTemplate(),
                )

    def generate_core_lib_class(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/{self.snake_core_lib_name}.py',
            {
                'data_access': self.core_lib_data_access,
                'jobs': self.core_lib_jobs,
                'cache': self.core_lib_cache,
                'config': self.core_lib_config,
            },
            CoreLibClassGenerateTemplate(),
        )

    def generate_config(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/config/{self.snake_core_lib_name}.yaml',
            self.core_lib_config,
            ConfigGenerateTemplate(),
        )

    def generate_hydra_plugins(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/hydra_plugins/{self.snake_core_lib_name}/{self.snake_core_lib_name}_sourcepath.py',
            {},
            HydraPluginsGenerateTemplate(),
        )

    def generate_git_ignore(self):
        self._generate_template(f'{self.snake_core_lib_name}/.gitignore', {}, GitIgnoreGenerateTemplate())

    def generate_docker_ignore(self):
        self._generate_template(f'{self.snake_core_lib_name}/.dockerignore', {}, DockerIgnoreGenerateTemplate())

    def generate_readme(self):
        self._generate_template(f'{self.snake_core_lib_name}/README.md', {}, ReadmeGenerateTemplate())

    def generate_requirements(self):
        self._generate_template(f'{self.snake_core_lib_name}/requirements.txt', {}, RequirementsGenerateTemplate())

    def generate_default_config(self):
        self._generate_template(f'{self.snake_core_lib_name}/core_lib_config.yaml', {}, DefaultConfigGenerateTemplate())

    def generate_manifest(self):
        self._generate_template(f'{self.snake_core_lib_name}/MANIFEST.in', {}, ManifestGenerateTemplate())

    def generate_setup(self):
        if self.core_lib_setup:
            self._generate_template(f'{self.snake_core_lib_name}/setup.py', self.core_lib_setup, SetupGenerateTemplate())
            self._generate_template(
                f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/__init__.py',
                self.core_lib_setup,
                VersionGenerateTemplate(),
            )
            utc_now = datetime.utcnow()
            self._generate_template(
                f'{self.snake_core_lib_name}/LICENSE_{utc_now.year}_{utc_now.month}_{utc_now.day}',
                self.core_lib_setup,
                LicenseGenerateTemplate(),
            )

    def run_all(self):
        self.generate_data_access()
        self.generate_entities()
        self.generate_jobs()
        self.generate_core_lib_class()
        self.generate_config()
        self.generate_hydra_plugins()
        self.generate_git_ignore()
        self.generate_docker_ignore()
        self.generate_readme()
        self.generate_requirements()
        self.generate_default_config()
        self.generate_manifest()
        self.generate_setup()
