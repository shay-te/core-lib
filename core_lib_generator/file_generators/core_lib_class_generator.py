from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.string import camel_to_snake, snake_to_camel
from core_lib_generator.file_generators.template_generator import TemplateGenerator
from core_lib_generator.generator_utils.formatting_utils import add_tab_spaces, remove_line
from core_lib_generator.generator_utils.helpers import unsupported_connection_type
from core_lib_generator.generator_utils.naming_utils import (
    data_access_attribute_name,
    service_attribute_name,
    service_module_name,
)


class CoreLibClassGenerateTemplate(TemplateGenerator):
    def generate(self, template_content: str, yaml_data: dict, core_lib_name: str, file_name: str) -> str:
        data_access_list = []
        if get_dict_attr(yaml_data, 'data_access'):
            [data_access_list.append(get_dict_attr(da, 'key')) for da in get_dict_attr(yaml_data, 'data_access')]
        updated_file = template_content.replace('Template', snake_to_camel(core_lib_name))
        if get_dict_attr(yaml_data, 'connections'):
            updated_file = _add_connections(updated_file, yaml_data, core_lib_name)
            updated_file = _add_alembic_funcs(updated_file, get_dict_attr(yaml_data, 'connections'), core_lib_name)
        else:
            updated_file = remove_line('# template_alembic_imports', updated_file)
            updated_file = remove_line('# template_alembic_functions', updated_file)
            updated_file = remove_line('# template_connections_imports', updated_file)
            updated_file = remove_line('# template_connections', updated_file)
        if data_access_list:
            updated_file = _add_data_access(updated_file, yaml_data, core_lib_name, data_access_list)
        else:
            updated_file = remove_line('# template_da_imports', updated_file)
            updated_file = remove_line('# template_da_instances', updated_file)
        if get_dict_attr(yaml_data, 'services'):
            updated_file = _add_service(updated_file, yaml_data, core_lib_name)
        else:
            updated_file = remove_line('# template_service_imports', updated_file)
            updated_file = remove_line('# template_service_instances', updated_file)
        if get_dict_attr(yaml_data, 'cache'):
            updated_file = _add_cache(updated_file, yaml_data, core_lib_name)
        else:
            updated_file = remove_line('# template_cache_handler_imports', updated_file)
            updated_file = remove_line('# template_cache_handlers', updated_file)
        if get_dict_attr(yaml_data, 'jobs'):
            updated_file = _add_job(updated_file, yaml_data, core_lib_name)
        else:
            updated_file = remove_line('# template_jobs_data_handlers', updated_file)
            updated_file = remove_line('# template_load_jobs', updated_file)
        return updated_file

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/template_core_lib/template_core_lib.py'


def _create_data_access_imports(data_access_list: list, core_lib_name: str) -> str:
    da_imports = []
    for da_name in data_access_list:
        da_imports.append(f'from {core_lib_name}.data_layers.data_access.{camel_to_snake(da_name)} import {da_name}')
    return '\n'.join(da_imports)


def _add_connections(template_content: str, yaml_data: dict, core_lib_name: str) -> str:
    handler_list = []
    imports_list = []
    updated_file = template_content
    connections = get_dict_attr(yaml_data, 'connections')
    for connection in connections:
        conn_key = connection['key']
        conn_type = connection['type'].split('.')[-1]
        config_instantiate = get_dict_attr(connection, 'config_instantiate')
        instantiate = 'instantiate_config' if config_instantiate else conn_type
        if instantiate == 'instantiate_config':
            imports_list.append('from core_lib.helpers.config_instances import instantiate_config')
        handler_str = ''
        if 'SqlAlchemyConnectionFactory' in conn_type:
            if not config_instantiate:
                imports_list.append('from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory')
            handler_str = f'{conn_key} = {instantiate}(self.config.core_lib.{core_lib_name}.data.{conn_key})'
        elif 'SolrConnectionFactory' in conn_type:
            if not config_instantiate:
                imports_list.append('from core_lib.connection.solr_connection_factory import SolrConnectionFactory')
            handler_str = f'{conn_key} = {instantiate}(self.config.core_lib.{core_lib_name}.solr.{conn_key})'
        elif 'Neo4jConnectionFactory' in conn_type:
            if not config_instantiate:
                imports_list.append('from core_lib.connection.neo4j_connection_factory import Neo4jConnectionFactory')
            handler_str = f'{conn_key} = {instantiate}(self.config.core_lib.{core_lib_name}.neo4j.{conn_key})'
        else:
            raise unsupported_connection_type(conn_key, connection['type'])
        handler_list.append(add_tab_spaces(handler_str, 2))

    updated_file = updated_file.replace('# template_connections_imports', '\n'.join(dict.fromkeys(imports_list)))
    updated_file = updated_file.replace('# template_connections', '\n'.join(dict.fromkeys(handler_list)))
    return updated_file


def _add_data_access(template_content: str, yaml_data: dict, core_lib_name: str, data_access_list: list) -> str:
    inst_list = []
    updated_file = template_content
    yaml_data_dataaccess = get_dict_attr(yaml_data, 'data_access')
    for data_access in yaml_data_dataaccess:
        # Without a connection, the DataAccess template has no __init__ to pass one to.
        connection = get_dict_attr(data_access, 'connection') or ''
        da_name = get_dict_attr(data_access, 'key')
        inst_str = f'self.{data_access_attribute_name(da_name)} = {da_name}({connection})'
        inst_list.append(add_tab_spaces(inst_str, 2))
    updated_file = updated_file.replace(
        '# template_da_imports', _create_data_access_imports(data_access_list, core_lib_name)
    )
    updated_file = updated_file.replace('# template_da_instances', '\n'.join(inst_list))

    return updated_file


def _add_service(template_content: str, yaml_data: dict, core_lib_name: str) -> str:
    inst_list = []
    import_list = []
    updated_file = template_content
    services_list = get_dict_attr(yaml_data, 'services')
    for service in services_list:
        data_access = get_dict_attr(service, 'data_access')
        service_name = get_dict_attr(service, 'key')
        data_access_instance = f'self.{data_access_attribute_name(data_access)}' if data_access else ''
        inst_str = f'self.{service_attribute_name(service_name)} = {service_name}({data_access_instance})'
        inst_list.append(add_tab_spaces(inst_str, 2))
        import_list.append(
            f'from {core_lib_name}.data_layers.service.{service_module_name(service_name)} import {service_name}')
    updated_file = updated_file.replace('# template_service_imports', '\n'.join(import_list))
    updated_file = updated_file.replace('# template_service_instances', '\n'.join(inst_list))
    return updated_file


def _add_cache(template_content: str, yaml_data: dict, core_lib_name: str) -> str:
    updated_file = template_content
    cache_imports = []
    cache_inits = []
    yaml_data_cache = get_dict_attr(yaml_data, 'cache')
    for cache in yaml_data_cache:
        name = get_dict_attr(cache, 'key')
        cache_type = get_dict_attr(cache, 'type')
        if cache_type == 'memory':
            cache_imports.append(f'from core_lib.cache.cache_handler_ram import CacheHandlerRam')
            cache_str = f'CoreLib.cache_registry.register(\'{name}\', CacheHandlerRam())'
            cache_inits.extend(_guarded_registration(name, cache_str))
        elif cache_type == 'memcached':
            cache_imports.append('from core_lib.data_layers.data.data_helpers import build_url')
            cache_imports.append('from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached')
            cache_str = f'CoreLib.cache_registry.register(\'{name}\', CacheHandlerMemcached(build_url(**self.config.core_lib.{core_lib_name}.cache.{name}.url)))'
            cache_inits.extend(_guarded_registration(name, cache_str))
        elif cache_type == 'redis':
            cache_imports.append('from core_lib.data_layers.data.data_helpers import build_url')
            cache_imports.append('from core_lib.cache.cache_handler_redis import CacheHandlerRedis')
            cache_str = f'CoreLib.cache_registry.register(\'{name}\', CacheHandlerRedis(build_url(**self.config.core_lib.{core_lib_name}.cache.{name}.url)))'
            cache_inits.extend(_guarded_registration(name, cache_str))
        else:
            raise ValueError(
                f'cache `{name}` has an unsupported type `{cache_type}`; '
                'the generator supports memory, memcached, redis'
            )
    updated_file = updated_file.replace(
        '# template_cache_handler_imports',
        '\n'.join(dict.fromkeys(cache_imports)),
    )
    updated_file = updated_file.replace(
        '# template_cache_handlers',
        '\n'.join(cache_inits),
    )
    return updated_file


def _guarded_registration(name: str, register_str: str) -> list:
    # The cache registry is process-wide, so a second construction must not register the name again.
    return [
        add_tab_spaces(f'if not CoreLib.cache_registry.get(\'{name}\'):', 2),
        add_tab_spaces(register_str, 3),
    ]


def _add_job(template_content: str, yaml_data: dict, core_lib_name: str) -> str:
    updated_file = template_content
    job_handler = {}
    job_handler_str = f'jobs_data_handlers = {str(job_handler)}'
    load_jobs_str = f'self.load_jobs(self.config.core_lib.{core_lib_name}.jobs, jobs_data_handlers)'
    updated_file = updated_file.replace('# template_jobs_data_handlers', add_tab_spaces(job_handler_str, 2))
    updated_file = updated_file.replace('# template_load_jobs', add_tab_spaces(load_jobs_str, 2))
    return updated_file


def _add_alembic_funcs(template_content: str, yaml_data: dict, core_lib_name: str) -> str:
    updated_file = template_content
    add_func = False
    for connection in yaml_data:
        if get_dict_attr(connection, 'migrate'):
            add_func = True
    if add_func:
        imports_list = ['import os', 'import inspect', 'from core_lib.alembic.alembic import Alembic']
        func_list = []
        camel_core_lib = snake_to_camel(core_lib_name)
        static_method_str = '@staticmethod'
        install_func_str = 'def install(cfg: DictConfig):'
        upgrade_alembic_str = f'Alembic(os.path.dirname(inspect.getfile({camel_core_lib})), cfg).upgrade()'
        func_list.append(add_tab_spaces(static_method_str))
        func_list.append(add_tab_spaces(install_func_str))
        func_list.append(add_tab_spaces(upgrade_alembic_str, 2))
        func_list.append('')

        uninstall_func_str = 'def uninstall(cfg: DictConfig):'
        downgrade_alembic_str = f'Alembic(os.path.dirname(inspect.getfile({camel_core_lib})), cfg).downgrade()'
        func_list.append(add_tab_spaces(static_method_str))
        func_list.append(add_tab_spaces(uninstall_func_str))
        func_list.append(add_tab_spaces(downgrade_alembic_str, 2))
        updated_file = updated_file.replace('# template_alembic_imports', '\n'.join(imports_list))
        func_list_join = '\n'.join(func_list)
        updated_file = updated_file.replace('# template_alembic_functions', f'\n{func_list_join}')
    else:
        updated_file = remove_line('# template_alembic_imports', updated_file)
        updated_file = remove_line('# template_alembic_functions', updated_file)
    return updated_file
