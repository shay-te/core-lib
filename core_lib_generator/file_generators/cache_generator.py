import os
import shutil

from core_lib_generator.file_generators.template_generate import TemplateGenerate
from core_lib_generator.generator_file_utils import replace_file_strings, replace_file_line


class CacheGenerateTemplate(TemplateGenerate):
    def handle(self, template_file: str, yaml_data: dict):
        cache_type = yaml_data['type']
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
            host = yaml_data['host']
            port = yaml_data['port']
            cache_str = f'CoreLib.cache_registry.register(\'memcached_cache\', CacheHandlerMemcached(build_url(host=\'{host}\', port={port})))'
            replace_file_line(filename, '# template_cache_handler', cache_str.rjust(len(cache_str) + 8))
        else:
            pass

    def get_template_file(self, yaml_data: dict) -> str:
        return 'template_core_lib/core_lib/template_core_lib.py'
