import enum

from core_lib.helpers.shell_utils import input_enum, input_int, input_str


class CacheTypes(enum.Enum):
    __order__ = 'Memcached Memory Empty'
    Memcached = 1
    Memory = 2
    Empty = 3


def generate_cache_template() -> dict:
    cache_type = input_enum(
        CacheTypes, 'From the following list, select the relevant number for cache type', CacheTypes.Memory.value
    )

    if cache_type == CacheTypes.Memcached.value:
        memcache_port = input_int('Enter your memcached server port no.', 11211)
        memcache_host = input_str('Enter your memcached server host', 'localhost')
        print(f'Cache type {CacheTypes(cache_type).name} on {memcache_host}:{memcache_port}')
        return {
            'env': {
                'MEMCACHED_HOST': memcache_host,
                'MEMCACHED_PORT': memcache_port,
            },
            'config': {
                'type': CacheTypes(cache_type).name.lower(),
                'url': {
                    'host': f'${{oc.env:MEMCACHED_HOST}}',
                    'port': f'${{oc.env:MEMCACHED_PORT}}',
                },
            },
        }
    elif cache_type == CacheTypes.Memory.value:
        print(f'Cache type {CacheTypes(cache_type).name}')
        return {
            'config': {
                'type': CacheTypes(cache_type).name.lower(),
            }
        }
    else:
        print('No cache set.')
