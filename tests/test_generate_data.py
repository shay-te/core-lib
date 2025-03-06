import unittest
from datetime import datetime, timedelta

from core_lib.helpers.datetime_utils import reset_datetime
from core_lib.helpers.generate_data import generate_random_string, generate_email, generate_datetime
from core_lib.helpers.validation import is_email


def has_numbers(input_string: str):
    return any(char.isdigit() for char in input_string)


def has_uppercase(input_string: str):
    return any(char.isupper() for char in input_string)


def has_special_chars(input_string: str):
    return any(not c.isalnum() for c in input_string)


class TestGenerateData(unittest.TestCase):

    def test_generate_string(self):
        string = generate_random_string()
        self.assertEqual(10, len(string))
        self.assertFalse(has_uppercase(string))
        self.assertFalse(has_numbers(string))
        self.assertFalse(has_special_chars(string))

        string = generate_random_string(30, True)
        self.assertEqual(30, len(string))
        self.assertTrue(has_uppercase(string))
        self.assertFalse(has_numbers(string))
        self.assertFalse(has_special_chars(string))

        string = generate_random_string(30, True, True)
        self.assertEqual(30, len(string))
        self.assertTrue(has_uppercase(string))
        self.assertTrue(has_numbers(string))
        self.assertFalse(has_special_chars(string))

        string = generate_random_string(30, True, True, True)
        self.assertEqual(30, len(string))
        self.assertTrue(has_uppercase(string))
        self.assertTrue(has_numbers(string))
        self.assertTrue(has_special_chars(string))

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
