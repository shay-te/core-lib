import enum

from core_lib.helpers.shell_utils import input_enum, input_int, input_str


def generate_cache_template() -> dict:
    cache_name = input_str('Enter name for your cache')
    cache_type = input_enum(CacheTypes, 'From the following list, what cache will you use?', CacheTypes.Memory.value)

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
                cache_name: {
                    'type': CacheTypes(cache_type).name.lower(),
                    'url': {
                        'host': f'${{oc.env:MEMCACHED_HOST}}',
                        'port': f'${{oc.env:MEMCACHED_PORT}}',
                    },
                }
            },
        }
    elif cache_type == CacheTypes.Memory.value:
        print(f'Cache type {CacheTypes(cache_type).name}')
        return {
            'config': {
                cache_name: {
                    'type': CacheTypes(cache_type).name.lower(),
                }
            }
        }
    else:
        print('No cache set.')


class CacheTypes(enum.Enum):
    __order__ = 'Memcached Memory Empty'
    Memcached = 1
    Memory = 2
    Empty = 3
