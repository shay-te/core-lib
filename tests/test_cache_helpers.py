"""The checks the cache handlers share (`core_lib.cache.cache_helpers`), at their edges."""
import enum
import unittest
from datetime import datetime, timedelta

from core_lib.cache.cache_helpers import validate_json_cache_value, whole_expire

ONE_SECOND = timedelta(seconds=1)
ONE_MILLISECOND = timedelta(milliseconds=1)
ACCEPTED_VALUES = {
    'dict': {'b': 1, 'a': [None, True]},
    'list': ['acme', 1.5],
    'int': 42,
    'bool_is_an_int': True,
    'str': 'acme',
    'empty_str': '',
    'zero': 0,
}
REFUSED_VALUES = {
    'float': (1.5, "<class 'float'>"),
    'tuple': (('acme',), "<class 'tuple'>"),
    'set': ({'acme'}, "<class 'set'>"),
    'none': (None, "<class 'NoneType'>"),
    'bytes': (b'acme', "<class 'bytes'>"),
    'datetime': (datetime(2026, 1, 2), "<class 'datetime.datetime'>"),
}
NOT_POSITIVE_EXPIRES = (timedelta(0), timedelta(microseconds=-1), timedelta(seconds=-5), timedelta(days=-1))
WHOLE_SECONDS = {
    'one_second': (ONE_SECOND, 1),
    'thirty_days_and_a_second': (timedelta(days=30, seconds=1), 2_592_001),
    'one_year': (timedelta(days=365), 31_536_000),
    'built_from_milliseconds': (timedelta(milliseconds=3000), 3),
}
NOT_WHOLE_SECONDS = (timedelta(milliseconds=500), timedelta(seconds=1, microseconds=-1),
                     timedelta(seconds=1, microseconds=1), timedelta(days=365, microseconds=1))
WHOLE_MILLISECONDS = {
    'one_millisecond': (ONE_MILLISECOND, 1),
    'one_and_a_half_seconds': (timedelta(seconds=1, milliseconds=500), 1500),
    'one_year': (timedelta(days=365), 31_536_000_000),
    'built_from_microseconds': (timedelta(microseconds=7000), 7),
}
NOT_WHOLE_MILLISECONDS = (timedelta(microseconds=1), timedelta(microseconds=999),
                          timedelta(milliseconds=1, microseconds=1), timedelta(days=365, microseconds=1))


class WidgetKind(enum.IntEnum):
    ALPHA = 1


class TestCacheRules(unittest.TestCase):

    def test_a_json_value_is_accepted(self):
        for label, value in {**ACCEPTED_VALUES, 'int_enum_member': WidgetKind.ALPHA}.items():
            with self.subTest(label):
                self.assertIsNone(validate_json_cache_value(value))

    def test_a_value_outside_the_json_types_raises(self):
        for label, (value, type_text) in REFUSED_VALUES.items():
            with self.subTest(label), self.assertRaises(ValueError) as context:
                validate_json_cache_value(value)
            expected = 'result must be of type `dict`, `list`, `int` or `str`. got `{}`'.format(type_text)
            self.assertEqual(expected, str(context.exception))

    def test_a_whole_number_of_units_is_kept_exactly_as_an_int(self):
        cases = [(ONE_SECOND, 'seconds', WHOLE_SECONDS), (ONE_MILLISECOND, 'milliseconds', WHOLE_MILLISECONDS)]
        for unit, unit_name, expires in cases:
            for label, (expire, count) in expires.items():
                with self.subTest(unit=unit_name, expire=label):
                    result = whole_expire(expire, unit, unit_name)
                    self.assertEqual((int, count), (type(result), result))

    def test_an_expire_with_a_part_of_a_unit_raises(self):
        cases = [(ONE_SECOND, 'seconds', NOT_WHOLE_SECONDS), (ONE_MILLISECOND, 'milliseconds', NOT_WHOLE_MILLISECONDS)]
        for unit, unit_name, expires in cases:
            for expire in expires:
                with self.subTest(unit=unit_name, expire=repr(expire)), self.assertRaises(ValueError) as context:
                    whole_expire(expire, unit, unit_name)
                expected = 'expire must be a whole number of {}. got `{!r}`'.format(unit_name, expire)
                self.assertEqual(expected, str(context.exception))

    def test_an_expire_of_zero_or_less_raises(self):
        for expire in NOT_POSITIVE_EXPIRES:
            with self.subTest(repr(expire)), self.assertRaises(ValueError) as context:
                whole_expire(expire, ONE_SECOND, 'seconds')
            self.assertEqual('expire must be more than 0. got `{!r}`'.format(expire), str(context.exception))
