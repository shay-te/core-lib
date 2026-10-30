import string
import unittest
from datetime import datetime, timedelta

from core_lib.helpers.datetime_utils import reset_datetime
from core_lib.helpers.generate_data import generate_random_string, generate_email, generate_datetime
from core_lib.helpers.validation import is_email

LOWERCASE = set(string.ascii_lowercase)
UPPERCASE = set(string.ascii_uppercase)
DIGITS = set(string.digits)
PUNCTUATION = set(string.punctuation)

# A flag only widens the set characters are picked from, so a short string may lack that class.
# In 2000 picks the likeliest miss, no digit among 94 characters, has probability about 1e-98.
LONG_SAMPLE_LENGTH = 2000


class TestGenerateData(unittest.TestCase):

    def test_generate_string(self):
        generated = generate_random_string()
        self.assertEqual(10, len(generated))
        self.assertLessEqual(set(generated), LOWERCASE)

        generated = generate_random_string(30, True)
        self.assertEqual(30, len(generated))
        self.assertLessEqual(set(generated), LOWERCASE | UPPERCASE)

        generated = generate_random_string(30, True, True)
        self.assertEqual(30, len(generated))
        self.assertLessEqual(set(generated), LOWERCASE | UPPERCASE | DIGITS)

        generated = generate_random_string(30, True, True, True)
        self.assertEqual(30, len(generated))
        self.assertLessEqual(set(generated), LOWERCASE | UPPERCASE | DIGITS | PUNCTUATION)

    def test_generate_string_flags_add_their_characters(self):
        generated = generate_random_string(LONG_SAMPLE_LENGTH, upper=True, digits=True, special=True)

        for character_class in (LOWERCASE, UPPERCASE, DIGITS, PUNCTUATION):
            self.assertTrue(set(generated) & character_class)

    def test_generate_email(self):
        domain = 'example.com'
        email = generate_email(domain)
        self.assertIn(domain, email)
        self.assertTrue(is_email(email))

    def test_generate_datetime(self):
        today_sub_15 = reset_datetime(datetime.today() - timedelta(days=15))
        today_add_15 = reset_datetime(datetime.today() + timedelta(days=15))
        today_sub_10 = reset_datetime(datetime.today() - timedelta(days=10))
        today_add_10 = reset_datetime(datetime.today() + timedelta(days=10))
        today_sub_5 = reset_datetime(datetime.today() - timedelta(days=5))

        dattime = generate_datetime()
        self.assertIsInstance(dattime, datetime)
        self.assertTrue(today_sub_10 <= dattime <= today_add_10)
        self.assertFalse(today_add_10 < dattime < today_add_15)

        dattime = generate_datetime(today_sub_5)
        self.assertIsInstance(dattime, datetime)
        self.assertTrue(today_sub_5 <= dattime <= today_add_10)
        self.assertFalse(today_add_10 < dattime < today_add_15)

        dattime = generate_datetime(today_add_10, today_add_15)
        self.assertIsInstance(dattime, datetime)
        self.assertTrue(today_add_10 <= dattime <= today_add_15)
        self.assertFalse(today_sub_15 < dattime < today_sub_5)
