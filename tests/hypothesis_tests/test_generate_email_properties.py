"""Property-based tests for generate_data.generate_email."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.generate_data import generate_email
from tests.hypothesis_tests._settings import SETTINGS


_DOMAIN = st.text(
    alphabet=stringmod.ascii_lowercase + '.', min_size=3, max_size=30
).filter(lambda s: '.' in s and not s.startswith('.') and not s.endswith('.'))


class TestGenerateEmailProperties(unittest.TestCase):
    @given(domain=_DOMAIN)
    @SETTINGS
    def test_email_contains_at_and_domain(self, domain):
        email = generate_email(domain=domain)
        self.assertEqual(email.count('@'), 1)
        self.assertTrue(email.endswith('@' + domain))

    @given(domain=_DOMAIN)
    @SETTINGS
    def test_local_part_has_expected_length(self, domain):
        email = generate_email(domain=domain)
        local = email.split('@')[0]
        # generate_random_string default length is 10
        self.assertEqual(len(local), 10)

    @given(domain=_DOMAIN)
    @SETTINGS
    def test_local_part_is_lowercase_letters(self, domain):
        email = generate_email(domain=domain)
        local = email.split('@')[0]
        self.assertTrue(all(c in stringmod.ascii_lowercase for c in local))

    def test_default_domain(self):
        email = generate_email()
        self.assertTrue(email.endswith('@domain.com'))

    @given(domain=_DOMAIN, n=st.integers(min_value=2, max_value=5))
    @SETTINGS
    def test_multiple_calls_produce_unique_emails(self, domain, n):
        # Local part is random, so n calls should produce mostly-unique emails
        """
        Verify that multiple invocations of generate_email with the same domain produce different emails.
        """
        emails = {generate_email(domain=domain) for _ in range(n * 5)}
        # Very low probability of all collisions
        self.assertGreater(len(emails), 1)
