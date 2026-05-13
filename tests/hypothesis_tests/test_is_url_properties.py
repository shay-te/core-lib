"""Property-based tests for validation.is_url."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.validation import is_url
from tests.hypothesis_tests._settings import SETTINGS


_DOMAIN = st.text(alphabet=stringmod.ascii_lowercase, min_size=2, max_size=20)
_TLD = st.text(alphabet=stringmod.ascii_lowercase, min_size=2, max_size=6)


class TestIsUrlProperties(unittest.TestCase):
    @given(scheme=st.sampled_from(['http', 'https']), domain=_DOMAIN, tld=_TLD)
    @SETTINGS
    def test_well_formed_http_urls_accepted(self, scheme, domain, tld):
        self.assertTrue(is_url(f'{scheme}://{domain}.{tld}'))

    @given(scheme=st.sampled_from(['http', 'https']), domain=_DOMAIN, tld=_TLD,
           port=st.integers(min_value=1, max_value=65535))
    @SETTINGS
    def test_urls_with_port_accepted(self, scheme, domain, tld, port):
        self.assertTrue(is_url(f'{scheme}://{domain}.{tld}:{port}'))

    @given(
        scheme=st.sampled_from(['ftp', 'ssh', 'telnet', 'smtp', 'mailto']),
        domain=_DOMAIN,
        tld=_TLD,
    )
    @SETTINGS
    def test_non_http_schemes_rejected(self, scheme, domain, tld):
        self.assertFalse(is_url(f'{scheme}://{domain}.{tld}'))

    @given(text=st.text(alphabet=stringmod.ascii_letters + '.', min_size=1, max_size=30))
    @SETTINGS
    def test_no_scheme_rejected(self, text):
        if '://' not in text:
            self.assertFalse(is_url(text))

    def test_none_rejected(self):
        self.assertFalse(is_url(None))

    def test_empty_string_rejected(self):
        self.assertFalse(is_url(''))

    @given(a=st.integers(min_value=0, max_value=255), b=st.integers(min_value=0, max_value=255),
           c=st.integers(min_value=0, max_value=255), d=st.integers(min_value=0, max_value=255))
    @SETTINGS
    def test_ipv4_urls_accepted(self, a, b, c, d):
        self.assertTrue(is_url(f'http://{a}.{b}.{c}.{d}'))

    def test_localhost_accepted(self):
        self.assertTrue(is_url('http://localhost'))
        self.assertTrue(is_url('http://localhost:8080'))
