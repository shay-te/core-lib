import enum

from core_lib.data_transform.helpers import get_dict_attr
from core_lib.helpers.shell_utils import input_enum, input_int, input_str, input_yes_no


def generate_cache_template() -> list:
    cache_list = []

    def is_exists_cache(user_input: str) -> bool:
        for cache in cache_list:
            if get_dict_attr(cache, 'cache.key') == user_input:
                return False
        return True

    add_cache = True
    while add_cache:
        cache_name = input_str('Enter name for your cache', None, False, is_exists_cache)
        cache_type = input_enum(CacheTypes, 'From the following list, what cache will you use?',
                                CacheTypes.Memory.value)
        if cache_type == CacheTypes.Memory.value:
            print(f'Cache type {CacheTypes(cache_type).name}')
            cache_list.append({
                'cache': {
                    'key': cache_name,
                    'type': CacheTypes(cache_type).name.lower(),
                }
            })
        else:
            cache_type_name = CacheTypes(cache_type).name
            cache_port = input_int(f'Enter your {cache_type_name} server port no.', default_cache_ports[cache_type_name])
            cache_host = input_str(f'Enter your {cache_type_name} server host', 'localhost')
            cache_protocol = None
            if cache_type == CacheTypes.Redis.value:
                cache_protocol = input_str(f'Enter your {cache_type_name} protocol', f'{cache_type_name.lower()}')
            print(f'Cache type {cache_type_name} on {cache_host}:{cache_port}')
            cache_list.append(_generate_cache_config(cache_name, cache_type, cache_port, cache_host, cache_protocol))
        add_cache = input_yes_no('Do you want to add another cache', False)
    return cache_list


def _generate_cache_config(
    cache_name: str, cache_type: int, cache_port: int, cache_host: str, cache_protocol: str = None
):
    cache_type_name = CacheTypes(cache_type).name
    if cache_type == CacheTypes.Redis.value:
        return {
            'env': {
                f'{cache_name.upper()}_PORT': cache_port,
                f'{cache_name.upper()}_HOST': cache_host,
            },
            'cache': {
                'key': cache_name,
                'type': cache_type_name.lower(),
                'url': {
                    'host': f'${{oc.env:{cache_name.upper()}_HOST}}',
                    'port': f'${{oc.env:{cache_name.upper()}_PORT}}',
                    'protocol': cache_protocol,
                },
            },
        }
    else:
        return {
            'env': {
                f'{cache_name.upper()}_PORT': cache_port,
                f'{cache_name.upper()}_HOST': cache_host,
            },
            'cache': {
                'key': cache_name,
                'type': cache_type_name.lower(),
                'url': {
                    'host': f'${{oc.env:{cache_name.upper()}_HOST}}',
                    'port': f'${{oc.env:{cache_name.upper()}_PORT}}',
                },
            },
        }


class CacheTypes(enum.Enum):
    __order__ = 'Memcached Memory Redis'
    Memcached = 1
    Memory = 2
    Redis = 3


default_cache_ports = {
    CacheTypes.Memcached.name: 11211,
    CacheTypes.Redis.name: 6379,
}
