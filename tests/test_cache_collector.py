"""`core_lib generate` asks about caches; each answer becomes a cache entry of the library's YAML."""
import unittest

from core_lib_generator.config_collectors.cache import generate_cache_template
from tests.test_data.test_utils import typed


class TestCacheCollector(unittest.TestCase):

    def test_memory_cache_is_the_default_and_needs_no_server(self):
        # name, type [Enter = 2-Memory], another cache? [Enter = no]
        with typed('acme_cache', '', ''):
            caches = generate_cache_template()

        self.assertEqual([{'cache': {'key': 'acme_cache', 'type': 'memory'}}], caches)

    def test_redis_server_is_read_from_env_variables_named_after_the_cache(self):
        # type 3-Redis, then Enter for the port, host and protocol defaults
        with typed('sessions', '3', '', '', '', 'no'):
            caches = generate_cache_template()

        self.assertEqual([{
            'env': {'SESSIONS_PORT': 6379, 'SESSIONS_HOST': 'localhost'},
            'cache': {
                'key': 'sessions',
                'type': 'redis',
                'url': {'host': '${oc.env:SESSIONS_HOST}', 'port': '${oc.env:SESSIONS_PORT}', 'protocol': 'redis'},
            },
        }], caches)

    def test_typed_redis_server_replaces_every_default(self):
        with typed('sessions', '3', '6380', 'redis.acme.example', 'rediss', 'no'):
            caches = generate_cache_template()

        self.assertEqual({'SESSIONS_PORT': 6380, 'SESSIONS_HOST': 'redis.acme.example'}, caches[0]['env'])
        self.assertEqual('rediss', caches[0]['cache']['url']['protocol'])

    def test_memcached_is_asked_for_a_server_but_not_a_protocol(self):
        # type 1-Memcached: its own default port, and no protocol question (the next line answers "another cache?")
        with typed('pages', '1', '', 'cache.acme.example', 'no'):
            caches = generate_cache_template()

        self.assertEqual([{
            'env': {'PAGES_PORT': 11211, 'PAGES_HOST': 'cache.acme.example'},
            'cache': {
                'key': 'pages',
                'type': 'memcached',
                'url': {'host': '${oc.env:PAGES_HOST}', 'port': '${oc.env:PAGES_PORT}'},
            },
        }], caches)

    def test_a_cache_name_already_taken_is_asked_again(self):
        with typed('acme_cache', '', 'yes', 'acme_cache', 'pages', '2', 'no'):
            caches = generate_cache_template()

        self.assertEqual(
            [{'cache': {'key': 'acme_cache', 'type': 'memory'}}, {'cache': {'key': 'pages', 'type': 'memory'}}],
            caches,
        )
