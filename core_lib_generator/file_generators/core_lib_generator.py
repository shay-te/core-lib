from core_lib.helpers.string import camel_to_snake, snake_to_camel
from core_lib_generator.file_generators.template_generate import TemplateGenerate


class CoreLibGenerateTemplate(TemplateGenerate):
    def generate(self, template_file: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        data_access_list = list(yaml_data['data_access'].keys())
        new_file = template_file.replace('TemplateCoreLib', snake_to_camel(core_lib_name))
        if data_access_list:
            new_file = _add_data_access(new_file, yaml_data, core_lib_name, data_access_list)
        if yaml_data['cache']:
            new_file = _add_cache(new_file, yaml_data, core_lib_name)
        if yaml_data['jobs']:
            new_file = _add_job(new_file, yaml_data, core_lib_name)
        return new_file

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/core_lib/template_core_lib.py'


def _create_data_access_imports(data_access_list: list, core_lib_name: str) -> str:
    da_imports = []
    for da_name in data_access_list:
        da_imports.append(
            f'from {core_lib_name}.core_lib.data_layers.data_access.{camel_to_snake(da_name)} import {da_name}'
        )
    return '\n'.join(da_imports)


def _create_job_imports(job_list: list, core_lib_name: str, jobs: dict) -> str:
    job_imports = []
    for job_name in job_list:
        class_name = jobs[job_name]['class_name']
        job_imports.append(f'from {core_lib_name}.core_lib.jobs.{job_name.lower()} import {class_name}')
    return '\n'.join(job_imports)


def _add_data_access(template_file: str, yaml_data: dict, core_lib_name: str, data_access_list: list) -> str:
    inst_list = []
    handler_list = []
    new_file = template_file
    for name in yaml_data['data_access']:
        entity = yaml_data['data_access'][name]['entity']
        db_connection = yaml_data['data_access'][name]['db_connection']
        inst_str = f'self.{entity.lower()} = {name}({db_connection}_session)'
        inst_list.append(inst_str.rjust(len(inst_str) + 8))
        handler_str = f'{db_connection}_session = SqlAlchemyDataHandlerRegistry(self.config.core_lib.{core_lib_name}.data.{db_connection})'
        handler_list.append(handler_str.rjust(len(handler_str) + 8))
    new_file = new_file.replace(
        '# template_da_imports',
        _create_data_access_imports(data_access_list, core_lib_name)
    )
    new_file = new_file.replace(
        '# template_data_handlers_imports',
        'from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry',
    )
    new_file = new_file.replace('# template_da_instances', '\n'.join(inst_list))
    new_file = new_file.replace('# template_data_handlers', '\n'.join(set(handler_list)))
    return new_file


def _add_cache(template_file: str, yaml_data: dict, core_lib_name: str) -> str:
    cache_type = yaml_data['cache']['type']
    new_file = template_file
    if cache_type == 'memory':
        new_file = new_file.replace(
            '# template_cache_handler_imports',
            f'from core_lib.cache.cache_handler_ram import CacheHandlerRam',
        )
        cache_str = f'CoreLib.cache_registry.register(\'memory_cache\', CacheHandlerRam())'
        new_file = new_file.replace('# template_cache_handler', cache_str.rjust(len(cache_str) + 8))
    elif cache_type == 'memcached':
        cache_imports = [
            'from core_lib.data_layers.data.data_helpers import build_url',
            'from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached',
        ]
        new_file = new_file.replace(
            '# template_cache_handler_imports',
            '\n'.join(cache_imports),
        )
        cache_str = f'CoreLib.cache_registry.register(\'memcached_cache\', CacheHandlerMemcached(build_url(host=self.config.core_lib.{core_lib_name}.cache.url.host, port=self.config.core_lib.{core_lib_name}.cache.url.port)))'
        new_file = new_file.replace('# template_cache_handler', cache_str.rjust(len(cache_str) + 8))
    else:
        pass
    return new_file


def _add_job(template_file: str, yaml_data: dict, core_lib_name: str) -> str:
    new_file = template_file
    job_list = list(yaml_data['jobs'].keys())
    job_handler = {}
    job_handler_str = f'jobs_data_handlers = {str(job_handler)}'
    load_jobs_str = f'self.load_jobs(self.config.core_lib.{core_lib_name}.jobs, jobs_data_handlers)'
    new_file = new_file.replace(
        '# template_jobs_data_handlers',
        job_handler_str.rjust(len(job_handler_str) + 8)
    )
    new_file = new_file.replace(
        '# template_load_jobs',
        load_jobs_str.rjust(len(load_jobs_str) + 8)
    )
    return new_file
