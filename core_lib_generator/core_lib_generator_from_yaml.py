import os
from datetime import datetime

from omegaconf import DictConfig

from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.string import camel_to_snake
from core_lib_generator.file_generators.config_generator import ConfigGenerateTemplate
from core_lib_generator.file_generators.core_lib_class_generator import CoreLibClassGenerateTemplate
from core_lib_generator.file_generators.default_config_generator import DefaultConfigGenerateTemplate
from core_lib_generator.file_generators.dockerignore_generator import DockerIgnoreGenerateTemplate
from core_lib_generator.file_generators.env_generator import EnvGenerateTemplate
from core_lib_generator.file_generators.gitignore_generator import GitIgnoreGenerateTemplate
from core_lib_generator.file_generators.hydra_plugins_generator import HydraPluginsGenerateTemplate
from core_lib_generator.file_generators.data_access_generator import DataAccessGenerateTemplate
from core_lib_generator.file_generators.entity_generator import EntityGenerateTemplate
from core_lib_generator.file_generators.jobs_generator import JobsGenerateTemplate
from core_lib_generator.file_generators.license_generator import LicenseGenerateTemplate
from core_lib_generator.file_generators.manifest_generator import ManifestGenerateTemplate
from core_lib_generator.file_generators.readme_generator import ReadmeGenerateTemplate
from core_lib_generator.file_generators.requirements_generator import RequirementsGenerateTemplate
from core_lib_generator.file_generators.service_generator import ServiceGenerateTemplate
from core_lib_generator.file_generators.setup_generator import SetupGenerateTemplate
from core_lib_generator.file_generators.template_core_lib_instance_generator import CoreLibInstanceGenerate
from core_lib_generator.file_generators.template_generator import TemplateGenerator
from core_lib_generator.file_generators.test_config_generator import TestConfigGenerateTemplate
from core_lib_generator.file_generators.test_config_override_generator import TestConfigOverrideGenerateTemplate
from core_lib_generator.file_generators.test_generator import TestGenerateTemplate
from core_lib_generator.file_generators.test_util_generator import UtilTestGenerateTemplate
from core_lib_generator.file_generators.version_generator import VersionGenerateTemplate


class CoreLibGenerator:
    def __init__(self, config: DictConfig):
        self.core_lib_name = config.core_lib.name
        self.snake_core_lib_name = camel_to_snake(self.core_lib_name)

        self.core_lib_env = get_dict_attr(config['core_lib'], 'env')
        self.core_lib_connections = get_dict_attr(config['core_lib'], 'connections')
        self.core_lib_entities = get_dict_attr(config['core_lib'], 'entities')
        self.core_lib_data_accesses = get_dict_attr(config['core_lib'], 'data_accesses')
        self.core_lib_jobs = get_dict_attr(config['core_lib'], 'jobs')
        self.core_lib_caches = get_dict_attr(config['core_lib'], 'caches')
        self.core_lib_setup = get_dict_attr(config['core_lib'], 'setup')
        self.core_lib_services = get_dict_attr(config['core_lib'], 'services')
        self.core_lib_server_type = get_dict_attr(config['core_lib'], 'server_type')

    def _generate_template(
            self, file_path: str, yaml_data: dict, template_generator: TemplateGenerator, file_name: str = None
    ):
        file_dir_path = os.path.dirname(file_path)
        if not file_dir_path:
            file_dir_path = '.'
        os.makedirs(file_dir_path, exist_ok=True)
        excluded_init_dirs = template_generator.exclude_init_from_dirs()
        dir_names = file_dir_path.split('/')
        init_path = ''
        for filename in dir_names:
            init_path = os.path.join(init_path, filename)
            init_file_path = os.path.join(init_path, '__init__.py')
            if not os.path.isfile(init_file_path) and filename not in excluded_init_dirs:
                open(init_file_path, 'w').close()

        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.normpath(os.path.join(location, template_generator.get_template_file(yaml_data))), 'r') as template_file:
            new_file = template_generator.generate(template_file.read(), yaml_data, self.snake_core_lib_name, file_name)
        with open(file_path, 'w') as file:
            file.write(new_file)

    def generate_data_access(self):
        if self.core_lib_data_accesses:
            for da in self.core_lib_data_accesses:
                da_name = da['key']
                self._generate_template(
                    f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/data_layers/data_access/{camel_to_snake(da_name)}.py',
                    {
                        'data_access': da,
                        'connections': self.core_lib_connections,
                    },
                    DataAccessGenerateTemplate(),
                    da_name,
                )

    def generate_service(self):
        if self.core_lib_services:
            for service in self.core_lib_services:
                service_name = service['key']
                self._generate_template(
                    f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/data_layers/service/{camel_to_snake(service_name)}.py',
                    service,
                    ServiceGenerateTemplate(),
                    service_name,
                )

    def generate_entities(self):
        if self.core_lib_entities:
            for entity in self.core_lib_entities:
                entity_name = entity['key']
                conn_name = entity['connection']
                self._generate_template(
                    f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/data_layers/data/{conn_name}/entities/{entity_name.lower()}.py',
                    entity,
                    EntityGenerateTemplate(),
                    entity_name,
                )

    def generate_jobs(self):
        if self.core_lib_jobs:
            for job in self.core_lib_jobs:
                job_name = job['key']
                self._generate_template(
                    f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/jobs/{job_name}.py',
                    job,
                    JobsGenerateTemplate(),
                )

    def generate_core_lib_class(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/{self.snake_core_lib_name}.py',
            {
                'data_access': self.core_lib_data_accesses,
                'jobs': self.core_lib_jobs,
                'cache': self.core_lib_caches,
                'connections': self.core_lib_connections,
                'entities': self.core_lib_entities,
                'services': self.core_lib_services,
            },
            CoreLibClassGenerateTemplate(),
        )

    def generate_config(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/{self.snake_core_lib_name}/config/{self.snake_core_lib_name}.yaml',
            {
                'jobs': self.core_lib_jobs,
                'cache': self.core_lib_caches,
                'connections': self.core_lib_connections,
            },
            ConfigGenerateTemplate(),
        )

    def generate_hydra_plugins(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/hydra_plugins/{self.snake_core_lib_name}/{self.snake_core_lib_name}_searchpath.py',
            {},
            HydraPluginsGenerateTemplate(),
        )

    def generate_git_ignore(self):
        self._generate_template(f'{self.snake_core_lib_name}/.gitignore', {}, GitIgnoreGenerateTemplate())

    def generate_docker_ignore(self):
        self._generate_template(f'{self.snake_core_lib_name}/.dockerignore', {}, DockerIgnoreGenerateTemplate())

    def generate_readme(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/README.md', self.core_lib_data_accesses, ReadmeGenerateTemplate()
        )

    def generate_requirements(self):
        self._generate_template(f'{self.snake_core_lib_name}/requirements.txt', {}, RequirementsGenerateTemplate())

    def generate_default_config(self):
        self._generate_template(f'{self.snake_core_lib_name}/core_lib_config.yaml', {}, DefaultConfigGenerateTemplate())

    def generate_manifest(self):
        self._generate_template(f'{self.snake_core_lib_name}/MANIFEST.in', {}, ManifestGenerateTemplate())

    def generate_env(self):
        self._generate_template(f'{self.snake_core_lib_name}/.env', self.core_lib_env, EnvGenerateTemplate())

    def generate_setup(self):
        if self.core_lib_setup:
            self._generate_template(
                f'{self.snake_core_lib_name}/setup.py', self.core_lib_setup, SetupGenerateTemplate()
            )
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

    def generate_tests(self):
        self._generate_template(
            f'{self.snake_core_lib_name}/tests/test_{self.snake_core_lib_name}.py',
            {
                'services': self.core_lib_services,
                'data_accesses': self.core_lib_data_accesses,
            },
            TestGenerateTemplate(),
        )
        self._generate_template(
            f'{self.snake_core_lib_name}/tests/test_data/test_config/config.yaml',
            {},
            TestConfigGenerateTemplate(),
        )
        self._generate_template(
            f'{self.snake_core_lib_name}/tests/test_data/test_config/{self.snake_core_lib_name}_override.yaml',
            {},
            TestConfigOverrideGenerateTemplate(),
        )
        self._generate_template(f'{self.snake_core_lib_name}/tests/test_data/helpers/util.py',
                                {},
                                UtilTestGenerateTemplate(),
        )
        self._generate_template(f'{self.snake_core_lib_name}/{self.snake_core_lib_name}_instance.py',
                                {'server_type': self.core_lib_server_type},
                                CoreLibInstanceGenerate(),
        )

    def run_all(self):
        self.generate_data_access()
        self.generate_service()
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
        self.generate_env()
        self.generate_setup()
        self.generate_tests()
