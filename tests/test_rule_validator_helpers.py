import datetime
import unittest

from core_lib.rule_validator.helpers import (
    convert_datetime,
    convert_location,
    validate_location,
)


class TestConvertLocation(unittest.TestCase):
    def test_lat_lng_keys(self):
        self.assertEqual(convert_location({'lat': 1.0, 'lng': 2.0}), 'POINT(2.0 1.0)')

    def test_latitude_longitude_keys(self):
        self.assertEqual(
            convert_location({'latitude': 10.0, 'longitude': 20.0}), 'POINT(20.0 10.0)'
        )

    def test_none_returns_none(self):
        self.assertIsNone(convert_location(None))

    def test_empty_dict_returns_none(self):
        self.assertIsNone(convert_location({}))


class TestValidateLocation(unittest.TestCase):
    def test_valid_point_str(self):
        self.assertTrue(validate_location('POINT(20.0 10.0)'))

    def test_invalid_latitude_out_of_range(self):
        self.assertFalse(validate_location('POINT(20.0 91.0)'))

    def test_invalid_longitude_out_of_range(self):
        self.assertFalse(validate_location('POINT(181.0 10.0)'))

    def test_boundary_values(self):
        self.assertTrue(validate_location('POINT(180.0 90.0)'))
        self.assertTrue(validate_location('POINT(-180.0 -90.0)'))

    def test_empty_returns_true(self):
        self.assertTrue(validate_location(''))
        self.assertTrue(validate_location(None))


class TestConvertDatetime(unittest.TestCase):
    def test_int_timestamp(self):
        result = convert_datetime(0)
        self.assertIsNone(result)

    def test_positive_int_timestamp(self):
        result = convert_datetime(1000000)
        self.assertIsInstance(result, datetime.datetime)

    def test_float_timestamp(self):
        result = convert_datetime(1000000.5)
        self.assertIsInstance(result, datetime.datetime)

    def test_datetime_passthrough(self):
        dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
        self.assertEqual(convert_datetime(dt), dt)

    def test_date_converted_to_datetime(self):
        d = datetime.date(2024, 1, 1)
        result = convert_datetime(d)
        self.assertEqual(result, datetime.datetime(2024, 1, 1))

    def test_other_type_returns_value(self):
        self.assertEqual(convert_datetime('not a date'), 'not a date')

    def test_none_returns_none(self):
        self.assertIsNone(convert_datetime(None))
