import os
import shutil

from core_lib_generator.generator_file_utils import replace_file_strings, replace_file_line


def generate_cache(cache: dict, core_lib_name: str):
    filename = f'{core_lib_name}/{core_lib_name}/{core_lib_name}.py'
    cache_type = cache['type']
    if cache_type == 'memory':
        replace_file_line(
            filename,
            '# template_cache_handler_imports',
            f'from core_lib.cache.cache_handler_ram import CacheHandlerRam',
        )
        cache_str = f'CoreLib.cache_registry.register(\'memory_cache\', CacheHandlerRam())'
        replace_file_line(filename, '# template_cache_handler', cache_str.rjust(len(cache_str) + 8))
    elif cache_type == 'memcached':
        cache_imports = [
            'from core_lib.data_layers.data.data_helpers import build_url',
            'from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached',
        ]
        replace_file_line(
            filename,
            '# template_cache_handler_imports',
            '\n'.join(cache_imports),
        )
        host = cache['host']
        port = cache['port']
        cache_str = f'CoreLib.cache_registry.register(\'memcached_cache\', CacheHandlerMemcached(build_url(host=\'{host}\', port={port})))'
        replace_file_line(filename, '# template_cache_handler', cache_str.rjust(len(cache_str) + 8))
    else:
        pass
