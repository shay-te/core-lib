"""A plain `pip install core-lib` installs the core only; each optional backend is an extra that is enough to use it."""
import os
import re
import subprocess
import sys
import unittest

import core_lib
from tests.test_setup_packages import setup_arguments

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The last release line whose plain `pip install core-lib` installed every backend, Flask and Django.
LAST_ALL_IN_ONE_RELEASE = (0, 2)

# The modules each distribution installs: this table, not setup.py, decides what an extra makes importable.
DISTRIBUTION_MODULES = {
    'flask': ['flask', 'werkzeug'],
    'django': ['django'],
    'pyjwt': ['jwt'],
    'cryptography': ['cryptography'],
    'psycopg2-binary': ['psycopg2'],
    'pymysql': ['pymysql'],
    'pymongo': ['pymongo', 'bson'],
    'pysolr': ['pysolr'],
    'neo4j': ['neo4j'],
    'redis': ['redis'],
    'python-memcached': ['memcache'],
    'elasticsearch': ['elasticsearch', 'elastic_transport'],
    'geoalchemy2': ['geoalchemy2'],
    'shapely': ['shapely', 'numpy'],
}
OPTIONAL_MODULES = sorted({module for modules in DISTRIBUTION_MODULES.values() for module in modules})

# ES256 is the reason for cryptography: HS256 alone would pass without it.
JWT_ROUND_TRIP = (
    'from datetime import timedelta\n'
    'from cryptography.hazmat.primitives import serialization\n'
    'from cryptography.hazmat.primitives.asymmetric import ec\n'
    'from core_lib.session.jwt_token_handler import JWTTokenHandler\n'
    'for secret, algorithm in (("acme-test-secret-of-at-least-32-bytes", "HS256"), (ec.generate_private_key('
    'ec.SECP256R1()).private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, '
    'serialization.NoEncryption()), "ES256")):\n'
    '    handler = JWTTokenHandler(secret, timedelta(minutes=1), algorithm=algorithm)\n'
    '    assert handler.decode(handler.encode({"id": 1}))["id"] == 1, algorithm\n'
)


def web_usage(server_type: str, framework_setup: str = '') -> str:
    # The framework's helpers, a real response through them, and a login token.
    package = server_type.lower()
    return (
        framework_setup
        + f'import core_lib.web_helpers.{package}.require_login, core_lib.web_helpers.{package}.user_auth_middleware\n'
        'import core_lib.web_helpers.decorators\n'
        'from core_lib.web_helpers.request_response_helpers import response_json\n'
        'from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils\n'
        f'WebHelpersUtils.init(WebHelpersUtils.ServerType.{server_type})\n'
        'assert response_json({"id": 1}).status_code == 200\n'
        + JWT_ROUND_TRIP
    )


# What each extra must make work, run with every other optional module uninstalled.
EXTRA_USAGE = {
    'flask': web_usage('FLASK'),
    'django': web_usage('DJANGO', 'import django.conf; django.conf.settings.configure(COOKIE_NAME="acme_cookie")\n'),
    'jwt': JWT_ROUND_TRIP,
    'postgres': 'import sqlalchemy; sqlalchemy.create_engine("postgresql://reviewer:secret@127.0.0.1/acme")',
    'mysql': 'import sqlalchemy; sqlalchemy.create_engine("mysql+pymysql://reviewer:secret@127.0.0.1/acme")',
    'mongodb': 'import core_lib.connection.mongodb_connection_factory',
    'solr': 'import core_lib.connection.solr_connection_factory',
    'neo4j': 'import core_lib.connection.neo4j_connection_factory',
    'redis': 'import core_lib.cache.cache_handler_redis',
    'memcached': 'import core_lib.cache.cache_handler_memcached',
    'elasticsearch': 'import core_lib.connection.elasticsearch_connection_factory',
    # The WKB of POINT(1 2): converting it is what needs shapely.
    'geo': 'from geoalchemy2 import WKBElement\n'
           'from core_lib.data_transform.result_to_dict import result_to_dict\n'
           'where = WKBElement(bytes.fromhex("0101000000000000000000F03F0000000000000040"))\n'
           'assert result_to_dict({"where": where}) == {"where": {"latitude": 2.0, "longitude": 1.0}}',
}


def distribution_name(requirement: str) -> str:
    return re.split(r'[\[<>=!~; ]', requirement, maxsplit=1)[0].lower()


def run_with_only(modules: list, script: str) -> subprocess.CompletedProcess:
    blocked = [module for module in OPTIONAL_MODULES if module not in modules]
    prelude = 'import sys\n' + ''.join(f'sys.modules[{module!r}] = None\n' for module in blocked)
    environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
    return subprocess.run(
        [sys.executable, '-c', prelude + script], cwd=REPO_ROOT, env=environment, capture_output=True, text=True, timeout=120
    )


class TestSetupExtras(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        arguments = setup_arguments()
        cls.install_requires = arguments['install_requires']
        cls.extras_require = arguments.get('extras_require', {})

    def test_core_requirements_hold_no_optional_backend(self):
        core = {distribution_name(requirement) for requirement in self.install_requires}

        self.assertEqual(set(), core & set(DISTRIBUTION_MODULES))
        self.assertIn('sqlalchemy', core)
        self.assertIn('hydra-core', core)

    def test_every_backend_has_its_extra(self):
        self.assertEqual(set(EXTRA_USAGE) | {'all', 'test'}, set(self.extras_require))

    def test_each_extra_alone_is_enough_for_its_backend(self):
        for extra, script in EXTRA_USAGE.items():
            distributions = [distribution_name(requirement) for requirement in self.extras_require[extra]]
            unknown = [distribution for distribution in distributions if distribution not in DISTRIBUTION_MODULES]
            self.assertEqual([], unknown, extra)
            modules = [module for distribution in distributions for module in DISTRIBUTION_MODULES[distribution]]

            result = run_with_only(modules, script)

            self.assertEqual(0, result.returncode, f'[{extra}]\n{result.stderr[-3000:]}')

    def test_all_is_every_backend_extra(self):
        backends = {requirement for extra in EXTRA_USAGE for requirement in self.extras_require[extra]}

        self.assertEqual(sorted(backends), sorted(self.extras_require['all']))

    def test_split_ships_under_a_new_minor_version(self):
        # Removing installed dependencies breaks a consumer that declares plain `core-lib`, so it must not
        # reuse a 0.2.x version: `core-lib~=0.2.0` or `core-lib<0.3` must keep resolving to the old install.
        major, minor = (int(part) for part in core_lib.__version__.split('.')[:2])

        self.assertGreater((major, minor), LAST_ALL_IN_ONE_RELEASE)
