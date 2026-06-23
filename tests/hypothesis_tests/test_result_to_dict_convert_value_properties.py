"""Property-based tests for the type-conversion rules in result_to_dict.

Exercise every branch of __convert_value via dict inputs:
- enum.Enum → .value
- datetime.datetime → .timestamp()
- datetime.date → midnight timestamp
- WKBElement → Point.from_point_wkb (covered in example tests with mocks)
- Decimal → float
- everything else → unchanged
"""
import datetime
import enum
import unittest
from decimal import Decimal

from hypothesis import given, strategies as st

from core_lib.data_transform.result_to_dict import result_to_dict
from tests.hypothesis_tests._settings import SETTINGS


class _Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 'blue'


class TestResultToDictConvertValue(unittest.TestCase):
    @given(st.sampled_from(list(_Color)))
    @SETTINGS
    def test_enum_value_extracted(self, e):
        result = result_to_dict({'k': e})
        self.assertEqual(result['k'], e.value)

    @given(st.datetimes(
        min_value=datetime.datetime(1970, 1, 2),
        max_value=datetime.datetime(2099, 12, 30),
    ))
    @SETTINGS
    def test_datetime_converted_to_timestamp(self, dt):
        result = result_to_dict({'k': dt})
        self.assertEqual(result['k'], dt.timestamp())
        self.assertIsInstance(result['k'], float)

    @given(st.dates(
        min_value=datetime.date(1970, 1, 2),
        max_value=datetime.date(2099, 12, 30),
    ))
    @SETTINGS
    def test_date_converted_to_midnight_timestamp(self, d):
        result = result_to_dict({'k': d})
        expected = datetime.datetime(d.year, d.month, d.day).timestamp()
        self.assertEqual(result['k'], expected)

    @given(st.decimals(allow_nan=False, allow_infinity=False, min_value=-1e10, max_value=1e10))
    @SETTINGS
    def test_decimal_converted_to_float(self, dec):
        result = result_to_dict({'k': dec})
        self.assertEqual(result['k'], float(dec))
        self.assertIsInstance(result['k'], float)

    @given(st.integers())
    @SETTINGS
    def test_int_in_dict_unchanged(self, n):
        # __convert_value falls through for primitives
        result = result_to_dict({'k': n})
        self.assertEqual(result['k'], n)

    @given(st.text(min_size=1, max_size=20))
    @SETTINGS
    def test_str_in_dict_unchanged(self, s):
        result = result_to_dict({'k': s})
        self.assertEqual(result['k'], s)

    @given(st.booleans())
    @SETTINGS
    def test_bool_in_dict_unchanged(self, b):
        result = result_to_dict({'k': b})
        self.assertEqual(result['k'], b)

    def test_none_in_dict_unchanged(self):
        result = result_to_dict({'k': None})
        self.assertIsNone(result['k'])
