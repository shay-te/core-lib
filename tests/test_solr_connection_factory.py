"""`SolrConnectionFactory` must hand Solr credentials and a bounded timeout to pysolr.

`username`/`password` live BESIDE `url` in the config, so `build_url(**config.url)` never saw them
and the client connected anonymously. Nothing fails while Solr is unsecured, which is exactly why
it survived: setting `blockUnknown=true` would have 401'd every search at once, while an alias
healthcheck that does not authenticate either kept reporting green.

Each test is written so it FAILS against the pre-fix factory. A test that only passes against the
fixed code would not have distinguished the two.
"""
import ast
import inspect
import os
import re
import unittest
from unittest.mock import patch

from omegaconf import OmegaConf
from pysolr import Solr

import core_lib
from core_lib.connection import solr_connection_factory
from core_lib.connection.solr_connection_factory import SolrConnectionFactory

USERNAME = 'reviewer'
PASSWORD = 'sw0rdf1sh'

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONNECTION_DOCS = os.path.join(REPO_ROOT, 'docs', 'pages', 'core_lib_doc', 'Connection')
SOLR_PAGE = os.path.join(CONNECTION_DOCS, '4.solr_connection_registry.md')
CONNECTIONS_PAGE = os.path.join(CONNECTION_DOCS, '1.connection.md')
PACKAGED_CONFIG = os.path.join(os.path.dirname(core_lib.__file__), 'config', 'core_lib.yaml')
SECURED_SECTION = '## Secured Solr and timeouts'


def _config(**overrides):
    config = {
        'always_commit': True,
        'url': {'protocol': 'http', 'host': 'solr', 'port': 8983, 'path': 'solr/widgets'},
        'username': None,
        'password': None,
    }
    config.update(overrides)
    return OmegaConf.create(config)


def _read(path):
    with open(path, encoding='utf-8') as page:
        return page.read()


def _factory_source():
    return ast.parse(inspect.getsource(solr_connection_factory))


def _config_keys_the_factory_reads():
    keys = set()
    for node in ast.walk(_factory_source()):
        if isinstance(node, ast.Attribute) and getattr(node.value, 'id', None) == 'config':
            if node.attr != 'get':
                keys.add(node.attr)
        elif isinstance(node, ast.Call) and getattr(node.func, 'attr', None) == 'get':
            if getattr(node.func.value, 'id', None) == 'config':
                keys.add(node.args[0].value)
    return keys


def _keyword_names(solr_call):
    return {keyword.arg for keyword in solr_call.keywords}


class SolrConnectionFactoryTest(unittest.TestCase):

    def _build(self, config):
        with patch('core_lib.connection.solr_connection_factory.Solr') as solr:
            SolrConnectionFactory(config)
        self.assertEqual(solr.call_count, 1)
        return solr.call_args

    def test_credentials_are_passed_to_the_client(self):
        _, kwargs = self._build(_config(username=USERNAME, password=PASSWORD))
        self.assertEqual(kwargs['auth'], (USERNAME, PASSWORD))

    def test_credentials_are_NOT_folded_into_the_url(self):
        # `build_url` does not percent-encode, so a password containing `@` or `/` would corrupt
        # the URL — and a credential-bearing URL leaks into every SolrError message and debug log
        # line. Passing `auth=` keeps the secret out of anything that gets printed.
        args, _ = self._build(_config(username=USERNAME, password=PASSWORD))
        url = args[0]
        self.assertNotIn(PASSWORD, url)
        self.assertNotIn(USERNAME, url)
        self.assertEqual(url, 'http://solr:8983/solr/widgets')

    def test_an_unsecured_cluster_gets_no_auth(self):
        # The behaviour every current deployment relies on: absent credentials must not become an
        # empty-string basic-auth header, which a secured Solr rejects and an unsecured one ignores
        # — either way it would be a confusing failure mode to introduce.
        _, kwargs = self._build(_config())
        self.assertIsNone(kwargs['auth'])

    def test_empty_string_credentials_are_treated_as_absent(self):
        # These are read from env vars, and an UNSET env var lands as '' rather than None.
        _, kwargs = self._build(_config(username='', password=''))
        self.assertIsNone(kwargs['auth'])

    def test_missing_credential_keys_do_not_raise(self):
        # A consuming lib whose config predates these keys has no `username`/`password` node at
        # all. Attribute-style access would raise and break that lib's startup entirely, turning a
        # missing-credentials fix into a crash for everyone who did not need it.
        config = OmegaConf.create({
            'always_commit': True,
            'url': {'protocol': 'http', 'host': 'solr', 'port': 8983},
        })
        _, kwargs = self._build(config)
        self.assertIsNone(kwargs['auth'])

    def test_the_request_timeout_is_bounded_by_default(self):
        # pysolr defaults to 60s. A hung Solr would pin a request thread for a full minute, so a
        # slow index degrades into an app-wide outage.
        _, kwargs = self._build(_config())
        self.assertEqual(kwargs['timeout'], SolrConnectionFactory.DEFAULT_TIMEOUT_SECONDS)
        self.assertLess(SolrConnectionFactory.DEFAULT_TIMEOUT_SECONDS, 60)

    def test_an_explicit_timeout_wins(self):
        _, kwargs = self._build(_config(timeout=5))
        self.assertEqual(kwargs['timeout'], 5)

    def test_always_commit_is_still_forwarded(self):
        # Guards against the auth/timeout change dropping an argument that already worked.
        _, kwargs = self._build(_config(always_commit=False))
        self.assertFalse(kwargs['always_commit'])

    # The pages below describe this factory, and nothing else ties them to it: `Solr(...)` is
    # prose, so a new argument leaves it silently wrong. These read the factory's own source.

    def test_the_page_documents_the_call_the_factory_makes(self):
        documented = re.search(r'`(Solr\(build_url.*?\))`', _read(SOLR_PAGE)).group(1)
        documented_call = ast.parse(documented, mode='eval').body
        factory_calls = [
            node for node in ast.walk(_factory_source())
            if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'Solr'
        ]
        self.assertEqual(len(factory_calls), 1)
        self.assertEqual(_keyword_names(documented_call), _keyword_names(factory_calls[0]))

    def test_the_pages_name_every_config_key_the_factory_reads(self):
        keys = _config_keys_the_factory_reads()
        # Pins the walk itself, so a broken one cannot pass by finding nothing.
        self.assertEqual(keys, {'url', 'always_commit', 'username', 'password', 'timeout'})

        init_section = _read(SOLR_PAGE).split('### \\_\\_init\\_\\_()')[1].split('### get()')[0]
        overview = next(
            line for line in _read(CONNECTIONS_PAGE).splitlines()
            if line.startswith('Every factory except')
        )
        for key in keys:
            self.assertIn(f'`{key}`', init_section)
            self.assertRegex(overview, f'`{key}:?`')

    def test_the_page_states_the_real_default_timeouts(self):
        page = _read(SOLR_PAGE)
        ours = SolrConnectionFactory.DEFAULT_TIMEOUT_SECONDS
        pysolr_default = inspect.signature(Solr.__init__).parameters['timeout'].default
        self.assertIn(f"limits each request to {ours} seconds instead of pysolr's {pysolr_default}", page)
        self.assertIn(f"DEFAULT_TIMEOUT_SECONDS` ({ours}), not pysolr's {pysolr_default}", page)

    def test_the_documented_secured_config_builds_an_authenticated_client(self):
        section = _read(SOLR_PAGE).split(SECURED_SECTION)[1]
        block = re.search(r'```yaml\n(.*?)```', section, re.S).group(1)
        names = ('SOLR_HOST', 'SOLR_USERNAME', 'SOLR_PASSWORD')
        saved = {name: os.environ.get(name) for name in names}

        def restore():
            for name, value in saved.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        self.addCleanup(restore)
        os.environ.update(SOLR_HOST='solr', SOLR_USERNAME=USERNAME, SOLR_PASSWORD=PASSWORD)

        # Over the packaged defaults, as the page says a host composes it.
        config = OmegaConf.merge(OmegaConf.load(PACKAGED_CONFIG), OmegaConf.create(block))
        OmegaConf.set_struct(config, True)
        client = SolrConnectionFactory(config.core_lib.data.solr).client

        self.assertEqual(client.auth, (USERNAME, PASSWORD))
        self.assertEqual(client.url, 'http://solr:8983/solr/your_core')
        self.assertEqual(client.timeout, 5)

        # The same block on an unsecured Solr: the env vars are unset, so nothing is sent.
        del os.environ['SOLR_USERNAME'], os.environ['SOLR_PASSWORD']
        self.assertIsNone(SolrConnectionFactory(config.core_lib.data.solr).client.auth)

    def test_the_documented_minimal_config_uses_the_default_timeout(self):
        # The page's first block sets neither credentials nor a timeout.
        config = OmegaConf.create({'always_commit': True, 'url': {'protocol': 'http', 'host': 'solr'}})
        OmegaConf.set_struct(config, True)
        client = SolrConnectionFactory(config).client
        self.assertIsNone(client.auth)
        self.assertEqual(client.timeout, SolrConnectionFactory.DEFAULT_TIMEOUT_SECONDS)


if __name__ == '__main__':
    unittest.main()
