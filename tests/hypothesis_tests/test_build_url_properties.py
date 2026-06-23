"""Property-based tests for data_helpers.build_url."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.data_layers.data.data_helpers import build_url
from tests.hypothesis_tests._settings import SETTINGS


class TestBuildUrlProperties(unittest.TestCase):
    @given(
        protocol=st.sampled_from(['http', 'https', 'postgres', 'mongodb', 'redis']),
        host=st.text(alphabet=stringmod.ascii_lowercase, min_size=3, max_size=20),
        port=st.integers(min_value=1, max_value=65535),
    )
    @SETTINGS
    def test_well_formed_protocol_host_port(self, protocol, host, port):
        url = build_url(protocol=protocol, host=host, port=port)
        expected = f'{protocol}://{host}:{port}'
        self.assertEqual(url, expected)

    @given(
        username=st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10),
        password=st.text(
            alphabet=stringmod.ascii_letters + stringmod.digits,
            min_size=1,
            max_size=10,
        ),
    )
    @SETTINGS
    def test_credentials_format(self, username, password):
        url = build_url(
            protocol='proto', username=username, password=password, host='h'
        )
        self.assertEqual(url, f'proto://{username}:{password}@h')

    @given(
        path=st.text(alphabet=stringmod.ascii_letters + '/', min_size=1, max_size=20)
    )
    @SETTINGS
    def test_path_always_has_exactly_one_leading_slash(self, path):
        url = build_url(host='h', path=path)
        # `h` followed by `/` then the stripped path
        self.assertTrue(url.startswith('h/'))
        # Multiple leading slashes get collapsed to one
        self.assertFalse(url.startswith('h//'))

    @given(
        file=st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=15)
    )
    @SETTINGS
    def test_file_appended_after_slash(self, file):
        url = build_url(host='h', file=file)
        self.assertEqual(url, f'h/{file}')
