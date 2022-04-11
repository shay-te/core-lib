from core_lib.helpers.string import camel_to_snake, snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator


class CoreLibClassGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        data_access_list = list(yaml_data['data_access'].keys())
        updated_file = template_content.replace('Template', snake_to_camel(core_lib_name))
        if data_access_list:
            updated_file = _add_data_access(updated_file, yaml_data, core_lib_name, data_access_list)
        if yaml_data['cache']:
            updated_file = _add_cache(updated_file, yaml_data, core_lib_name)
        if yaml_data['jobs']:
            updated_file = _add_job(updated_file, yaml_data, core_lib_name)
        if yaml_data['config']:
            updated_file = _add_mongo(updated_file, yaml_data['config']['data'], core_lib_name)
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        return 'core_lib_generator/template_core_lib/template_core_lib/template_core_lib.py'


def _create_data_access_imports(data_access_list: list, core_lib_name: str) -> str:
    da_imports = []
    for da_name in data_access_list:
        da_imports.append(
            f'from {core_lib_name}.data_layers.data_access.{camel_to_snake(da_name)} import {da_name}'
        )
    return '\n'.join(da_imports)


def _add_data_access(template_content: str, yaml_data: dict, core_lib_name: str, data_access_list: list) -> str:
    inst_list = []
    handler_list = []
    updated_file = template_content
    for name in yaml_data['data_access']:
        entity = yaml_data['data_access'][name]['entity']
        db_connection = yaml_data['data_access'][name]['db_connection']
        inst_str = f'self.{db_connection}_{entity.lower()} = {name}({db_connection}_session)'
        inst_list.append(inst_str.rjust(len(inst_str) + 8))
        handler_str = f'{db_connection}_session = SqlAlchemyDataHandlerRegistry(self.config.core_lib.{core_lib_name}.data.{db_connection})'
        handler_list.append(handler_str.rjust(len(handler_str) + 8))
    updated_file = updated_file.replace(
        '# template_da_imports', _create_data_access_imports(data_access_list, core_lib_name)
    )
    updated_file = updated_file.replace(
        '# template_data_handlers_imports',
        'from core_lib.data_layers.data.handler.sql_alchemy_data_handler_registry import SqlAlchemyDataHandlerRegistry',
    )
    updated_file = updated_file.replace('# template_da_instances', '\n'.join(inst_list))
    updated_file = updated_file.replace('# template_data_handlers', '\n'.join(set(handler_list)))
    return updated_file


def _add_cache(template_content: str, yaml_data: dict, core_lib_name: str) -> str:
    updated_file = template_content
    cache_imports = []
    cache_inits = []
    for name in yaml_data['cache']:
        cache_type = yaml_data['cache'][name]['type']
        if cache_type == 'memory':
            cache_imports.append(f'from core_lib.cache.cache_handler_ram import CacheHandlerRam')
            cache_str = f'CoreLib.cache_registry.register(\'{name}\', CacheHandlerRam())'
            cache_inits.append(cache_str.rjust(len(cache_str) + 8))
        elif cache_type == 'memcached':
            cache_imports.append('from core_lib.data_layers.data.data_helpers import build_url')
            cache_imports.append('from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached')
            cache_str = f'CoreLib.cache_registry.register(\'{name}\', CacheHandlerMemcached(build_url(**self.config.core_lib.{core_lib_name}.{name}.cache.url)))'
            cache_inits.append(cache_str.rjust(len(cache_str) + 8))
        elif cache_type == 'redis':
            cache_imports.append('from core_lib.data_layers.data.data_helpers import build_url')
            cache_imports.append('from core_lib.cache.cache_handler_redis import CacheHandlerRedis')
            cache_str = f'CoreLib.cache_registry.register(\'{name}\', CacheHandlerRedis(build_url(**self.config.core_lib.{core_lib_name}.{name}.cache.url)))'
            cache_inits.append(cache_str.rjust(len(cache_str) + 8))
    updated_file = updated_file.replace(
        '# template_cache_handler_imports',
        '\n'.join(cache_imports),
    )
    updated_file = updated_file.replace(
        '# template_cache_handlers',
        '\n'.join(cache_inits),
    )
    return updated_file


def _add_job(template_content: str, yaml_data: dict, core_lib_name: str) -> str:
    updated_file = template_content
    job_handler = {}
    job_handler_str = f'jobs_data_handlers = {str(job_handler)}'
    load_jobs_str = f'self.load_jobs(self.config.core_lib.{core_lib_name}.jobs, jobs_data_handlers)'
    updated_file = updated_file.replace(
        '# template_jobs_data_handlers', job_handler_str.rjust(len(job_handler_str) + 8)
    )
    updated_file = updated_file.replace('# template_load_jobs', load_jobs_str.rjust(len(load_jobs_str) + 8))
    return updated_file


def _add_mongo(template_content: str, yaml_data: dict, core_lib_name: str) -> str:
    updated_file = template_content
    import_str = (
        'from core_lib.data_layers.data.handler.mongodb_data_handler_registry import MongoDBDataHandlerRegistry'
    )
    mongo_conn = []
    for db_connection in yaml_data:
        if yaml_data[db_connection]['url']['protocol'] == 'mongodb':
            conn_str = f'self.{db_connection}_session = MongoDBDataHandlerRegistry(self.config.core_lib.{core_lib_name}.data.{db_connection})'
            mongo_conn.append(conn_str.rjust(len(conn_str) + 8))
    if mongo_conn:
        updated_file = updated_file.replace('# template_mongo_handler_imports', import_str)
        updated_file = updated_file.replace(
            '# template_mongo_handlers',
            '\n'.join(mongo_conn),
        )
    return updated_file
