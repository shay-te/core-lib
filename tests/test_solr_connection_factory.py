"""`SolrConnectionFactory` must hand Solr credentials and a bounded timeout to pysolr.

`username`/`password` live BESIDE `url` in the config, so `build_url(**config.url)` never saw them
and the client connected anonymously. Nothing fails while Solr is unsecured, which is exactly why
it survived: setting `blockUnknown=true` would have 401'd every search at once, while an alias
healthcheck that does not authenticate either kept reporting green.

Each test is written so it FAILS against the pre-fix factory. A test that only passes against the
fixed code would not have distinguished the two.
"""
import unittest
from unittest.mock import patch

from omegaconf import OmegaConf

from core_lib.connection.solr_connection_factory import SolrConnectionFactory

USERNAME = 'reviewer'
PASSWORD = 'sw0rdf1sh'


def _config(**overrides):
    config = {
        'always_commit': True,
        'url': {'protocol': 'http', 'host': 'solr', 'port': 8983, 'path': 'solr/widgets'},
        'username': None,
        'password': None,
    }
    config.update(overrides)
    return OmegaConf.create(config)


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


if __name__ == '__main__':
    unittest.main()
