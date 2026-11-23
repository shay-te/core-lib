import itertools
import sys
import threading
import unittest
from collections import Counter
from datetime import datetime, timedelta

from core_lib.helpers.datetime_utils import reset_datetime
from core_lib.helpers.generate_data import generate_random_string, generate_email, generate_datetime
from core_lib.helpers.validation import is_email

# A requested kind was missed about once in 30 calls before the generator guaranteed it.
GENERATE_STRING_RUNS = 10_000
KIND_MATRIX_RUNS = 1_000
KIND_MATRIX_LENGTHS = (0, 1, 2, 3, 4, 10, 30, 1000)
FLAG_COMBINATIONS = tuple(itertools.product((False, True), repeat=3))
# Written out rather than read from `string`, which the generator itself uses.
LOWERCASE = frozenset('abcdefghijklmnopqrstuvwxyz')
UPPERCASE = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
DIGITS = frozenset('0123456789')
PUNCTUATION = frozenset('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
# Outcomes that must be equally likely; at these run counts their max/min count ratio stays near 1.06.
UNIFORMITY_RUNS = 20_000
MAX_COUNT_RATIO = 1.2
LONG_STRING_LENGTH = 100_000
MAX_SHARE_DIFFERENCE = 0.01
THREADS = 16
CALLS_PER_THREAD = 2_000
# A call takes microseconds, so threads interleave inside one only when they switch far more often than every 5ms.
THREAD_SWITCH_INTERVAL_SECONDS = 1e-6


def has_numbers(input_string: str):
    return any(char.isdigit() for char in input_string)


def has_uppercase(input_string: str):
    return any(char.isupper() for char in input_string)


def has_special_chars(input_string: str):
    return any(not c.isalnum() for c in input_string)


def requested_kinds(upper: bool, digits: bool, special: bool) -> list:
    return [kind for kind, flag in ((UPPERCASE, upper), (DIGITS, digits), (PUNCTUATION, special)) if flag]


def kind_of(char: str) -> frozenset:
    for kind in (LOWERCASE, UPPERCASE, DIGITS, PUNCTUATION):
        if char in kind:
            return kind
    return frozenset()


class TestGenerateData(unittest.TestCase):

    def test_generate_string(self):
        for _ in range(GENERATE_STRING_RUNS):
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

    def test_generate_string_every_kind_combination_and_length(self):
        for (upper, digits, special), length in itertools.product(FLAG_COMBINATIONS, KIND_MATRIX_LENGTHS):
            requested = requested_kinds(upper, digits, special)
            allowed = LOWERCASE.union(*requested)
            with self.subTest(upper=upper, digits=digits, special=special, length=length):
                for _ in range(KIND_MATRIX_RUNS):
                    string = generate_random_string(length, upper, digits, special)
                    self.assertIsInstance(string, str)
                    self.assertEqual(length, len(string))
                    self.assertLessEqual(set(string), allowed)
                    present = [kind for kind in requested if not kind.isdisjoint(string)]
                    self.assertEqual(min(length, len(requested)), len(present))

    def test_generate_string_shorter_than_the_requested_kinds(self):
        self.assertEqual('', generate_random_string(-1))
        self.assertEqual('', generate_random_string(-1, True, True, True))
        kept_kinds = Counter(kind_of(generate_random_string(1, True, True, True)) for _ in range(GENERATE_STRING_RUNS))
        self.assertEqual({UPPERCASE, DIGITS, PUNCTUATION}, set(kept_kinds))
        self.assertLess(max(kept_kinds.values()) / min(kept_kinds.values()), MAX_COUNT_RATIO)

    def test_generate_string_places_the_requested_kinds_in_any_order(self):
        orders = set()
        for _ in range(GENERATE_STRING_RUNS):
            orders.add(tuple(kind_of(char) for char in generate_random_string(3, True, True, True)))
        self.assertEqual(set(itertools.permutations((UPPERCASE, DIGITS, PUNCTUATION))), orders)

    def test_generate_string_draws_every_position_from_the_whole_pool(self):
        strings = [generate_random_string(30, True, True, True) for _ in range(GENERATE_STRING_RUNS)]
        self.assertTrue(any(string[0].islower() for string in strings))
        self.assertTrue(any(sum(char.isupper() for char in string) > 1 for string in strings))

    def test_generate_string_puts_a_requested_kind_at_every_position_equally_often(self):
        digits_at = Counter()
        for _ in range(UNIFORMITY_RUNS):
            string = generate_random_string(10, False, True)
            digits_at.update(position for position, char in enumerate(string) if char in DIGITS)
        counts = [digits_at[position] for position in range(10)]
        self.assertGreater(min(counts), 0)
        self.assertLess(max(counts) / min(counts), MAX_COUNT_RATIO)

    def test_generate_string_draws_each_character_of_a_kind_equally_often(self):
        for upper, digits, special in FLAG_COMBINATIONS:
            strings = [generate_random_string(30, upper, digits, special) for _ in range(UNIFORMITY_RUNS)]
            counts = Counter(''.join(strings))
            for kind in [LOWERCASE, *requested_kinds(upper, digits, special)]:
                with self.subTest(upper=upper, digits=digits, special=special, kind=''.join(sorted(kind))[:3]):
                    kind_counts = [counts[char] for char in kind]
                    self.assertGreater(min(kind_counts), 0)
                    self.assertLess(max(kind_counts) / min(kind_counts), MAX_COUNT_RATIO)

    def test_generate_string_draws_each_kind_in_proportion_to_its_size(self):
        string = generate_random_string(LONG_STRING_LENGTH, True, True, True)
        self.assertEqual(LONG_STRING_LENGTH, len(string))
        kinds = Counter(kind_of(char) for char in string)
        pool_size = len(LOWERCASE | UPPERCASE | DIGITS | PUNCTUATION)
        for kind in (LOWERCASE, UPPERCASE, DIGITS, PUNCTUATION):
            self.assertAlmostEqual(len(kind) / pool_size, kinds[kind] / LONG_STRING_LENGTH, delta=MAX_SHARE_DIFFERENCE)

    def test_generate_string_reads_a_falsy_flag_as_not_requested(self):
        self.assertLessEqual(set(generate_random_string(30, None, 0, '')), LOWERCASE)
        string = generate_random_string(3, 1, 1, 1)
        self.assertEqual({UPPERCASE, DIGITS, PUNCTUATION}, {kind_of(char) for char in string})

    def test_generate_string_from_many_threads_at_once(self):
        self.addCleanup(sys.setswitchinterval, sys.getswitchinterval())
        sys.setswitchinterval(THREAD_SWITCH_INTERVAL_SECONDS)
        strings = []

        def generate_many():
            for _ in range(CALLS_PER_THREAD):
                strings.append(generate_random_string(5, True, True, True))

        threads = [threading.Thread(target=generate_many) for _ in range(THREADS)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(THREADS * CALLS_PER_THREAD, len(strings))
        for string in strings:
            self.assertEqual(5, len(string))
            self.assertEqual({UPPERCASE, DIGITS, PUNCTUATION}, {kind_of(char) for char in string} - {LOWERCASE})

    def test_generate_email(self):
        domain = 'example.com'
        email = generate_email(domain)
        self.assertIn(domain, email)
        self.assertTrue(is_email(email))

    def test_generate_email_is_ten_lowercase_letters_at_the_domain(self):
        emails = ((generate_email(), 'domain.com'), (generate_email('mail.example.co.uk'), 'mail.example.co.uk'))
        for email, domain in emails:
            local_part, _, email_domain = email.partition('@')
            self.assertEqual(domain, email_domain)
            self.assertEqual(10, len(local_part))
            self.assertLessEqual(set(local_part), LOWERCASE)

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
