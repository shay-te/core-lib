"""The rule validator helpers: a location dict to WKT, WKT bounds, and timestamps or dates to datetimes."""
import datetime
import os
import time
import unittest

from core_lib.rule_validator.helpers import convert_datetime, convert_location, validate_location
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator

place_rule_validator = RuleValidator([
    ValueRuleValidator('location', dict, custom_converter=convert_location, custom_validator=validate_location),
])


class TestRuleValidatorHelpers(unittest.TestCase):

    def setUp(self):
        self._original_tz = os.environ.get('TZ')

    def tearDown(self):
        if self._original_tz is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = self._original_tz
        if hasattr(time, 'tzset'):
            time.tzset()

    def test_convert_location_reads_short_or_long_keys(self):
        self.assertEqual('POINT(34.7818 32.0853)', convert_location({'lat': 32.0853, 'lng': 34.7818}))
        self.assertEqual('POINT(34.7818 32.0853)', convert_location({'latitude': 32.0853, 'longitude': 34.7818}))
        self.assertEqual('POINT(34.7818 0)', convert_location({'latitude': 0, 'longitude': 34.7818}))
        self.assertIsNone(convert_location(None))
        self.assertIsNone(convert_location({}))

    def test_validate_location_checks_both_ranges_inclusively(self):
        expected = {
            'POINT(34.7818 32.0853)': True,
            'POINT(180 90)': True,
            'POINT(-180 -90)': True,
            'POINT(0 0)': True,
            'POINT(34.7818 90.0001)': False,
            'POINT(34.7818 -91)': False,
            'POINT(180.5 32)': False,
            'POINT(-181 32)': False,
        }
        for point, valid in expected.items():
            self.assertIs(valid, validate_location(point), point)
        self.assertIs(True, validate_location(None))

    def test_location_rule_stores_wkt_and_rejects_out_of_range(self):
        self.assertEqual(
            {'location': 'POINT(34.7818 32.0853)'},
            place_rule_validator.validate_dict({'location': {'lat': 32.0853, 'lng': 34.7818}}),
        )
        self.assertEqual({'location': None}, place_rule_validator.validate_dict({'location': None}))

        with self.assertRaises(PermissionError):
            place_rule_validator.validate_dict({'location': {'lat': 132.0, 'lng': 34.7818}})

        # Documented: a custom converter's own error is not turned into a PermissionError.
        with self.assertRaises(AttributeError):
            place_rule_validator.validate_dict({'location': '32.08,34.78'})

    def test_convert_datetime_keeps_datetimes_and_widens_dates(self):
        moment = datetime.datetime(2024, 6, 14, 9, 30)

        self.assertIs(moment, convert_datetime(moment))
        self.assertEqual(datetime.datetime(2024, 6, 14, 0, 0), convert_datetime(datetime.date(2024, 6, 14)))
        self.assertIs(datetime.datetime, type(convert_datetime(datetime.date(2024, 6, 14))))
        self.assertEqual('2024-06-14', convert_datetime('2024-06-14'))   # anything else is returned as is
        self.assertIsNone(convert_datetime(None))

    @unittest.skipUnless(hasattr(time, 'tzset'), 'time.tzset() is needed to change the process time zone')
    def test_convert_datetime_reads_a_unix_timestamp(self):
        os.environ['TZ'] = 'UTC'
        time.tzset()

        self.assertEqual(datetime.datetime(2024, 6, 14, 9, 30), convert_datetime(1718357400))
        self.assertEqual(datetime.datetime(2024, 6, 14, 9, 30, 0, 500000), convert_datetime(1718357400.5))
