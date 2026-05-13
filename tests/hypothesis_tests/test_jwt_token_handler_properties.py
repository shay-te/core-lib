"""Property-based tests for session.jwt_token_handler.JWTTokenHandler.

Invariant: encoding a dict and decoding the result should recover the dict's
keys (plus an added `exp` timestamp).
"""
import string as stringmod
import unittest
from datetime import timedelta

from hypothesis import given, strategies as st

from core_lib.session.jwt_token_handler import JWTTokenHandler
from tests.hypothesis_tests._settings import SETTINGS


_KEY_STRATEGY = st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10)
_VALUE_STRATEGY = st.one_of(
    st.text(min_size=1, max_size=20),
    st.integers(min_value=-10000, max_value=10000),
    st.booleans(),
)
_DICT_STRATEGY = st.dictionaries(
    keys=_KEY_STRATEGY,
    values=_VALUE_STRATEGY,
    min_size=1,
    max_size=10,
).filter(lambda d: 'exp' not in d)  # don't shadow the auto-added field


class TestJwtTokenHandlerProperties(unittest.TestCase):
    @given(_DICT_STRATEGY)
    @SETTINGS
    def test_encode_decode_recovers_payload(self, payload):
        # Copy because encode() mutates the payload (adds 'exp')
        original = dict(payload)
        handler = JWTTokenHandler('secret-key', timedelta(seconds=60))
        token = handler.encode(dict(payload))
        decoded = handler.decode(token)
        for k, v in original.items():
            self.assertEqual(decoded.get(k), v)

    @given(_DICT_STRATEGY)
    @SETTINGS
    def test_encode_adds_exp(self, payload):
        handler = JWTTokenHandler('secret', timedelta(seconds=60))
        encoded_payload = dict(payload)
        handler.encode(encoded_payload)
        self.assertIn('exp', encoded_payload)

    @given(_KEY_STRATEGY)
    @SETTINGS
    def test_decode_invalid_token_raises(self, garbage):
        handler = JWTTokenHandler('secret', timedelta(seconds=60))
        # Random ASCII strings are very unlikely to be valid JWTs
        with self.assertRaises(BaseException):
            handler.decode(garbage)
