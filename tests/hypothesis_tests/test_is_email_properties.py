"""Property-based tests for helpers.validation.is_email."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.validation import is_email
from tests.hypothesis_tests._settings import SETTINGS


class TestIsEmailProperties(unittest.TestCase):
    @given(s=st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=20))
    @SETTINGS
    def test_no_at_sign_rejects(self, s):
        if '@' not in s:
            self.assertFalse(is_email(s))

    @given(
        local=st.text(
            alphabet=stringmod.ascii_lowercase + stringmod.digits,
            min_size=1,
            max_size=10,
        ),
        domain=st.text(alphabet=stringmod.ascii_lowercase, min_size=2, max_size=10),
        tld=st.text(alphabet=stringmod.ascii_lowercase, min_size=2, max_size=4),
    )
    @SETTINGS
    def test_well_formed_email_accepted(self, local, domain, tld):
        email = f'{local}@{domain}.{tld}'
        self.assertTrue(is_email(email))

    @given(local=st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10))
    @SETTINGS
    def test_starts_with_dot_rejects(self, local):
        # Per regex: emails starting with '.' are rejected
        self.assertFalse(is_email(f'.{local}@example.com'))
