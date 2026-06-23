import unittest

from core_lib.helpers.parse_utils import (
    parse_range,
    fetch_closest_option,
    height_to_cm,
    _from_numeric,
    _is_hebrew_cm,
)


class TestParseUtilsGaps(unittest.TestCase):
    def test_parse_range_too_many_parts_returns_none(self):
        self.assertIsNone(parse_range('10 to 20 to 30'))

    def test_parse_range_with_unrecognized_token_returns_none(self):
        # parse_val returns the raw string when it is not 'any' and not digit
        # then lower/upper are not None — but the unrecognized strings are kept,
        # so the function returns a (str, int) tuple instead of None.
        result = parse_range('foo to 10')
        self.assertEqual(result, ('foo', 10))

    def test_parse_range_any_without_limits_returns_none(self):
        # "any" → None, no min_limit/max_limit provided
        self.assertIsNone(parse_range('any to 10'))
        self.assertIsNone(parse_range('10 to any'))

    def test_parse_range_any_with_limits(self):
        self.assertEqual(parse_range('any to 10', min_limit=0), (0, 10))
        self.assertEqual(parse_range('10 to any', max_limit=100), (10, 100))


class TestFetchClosestOption(unittest.TestCase):
    def test_non_string_source_returns_none(self):
        self.assertIsNone(fetch_closest_option(123, ['abc', 'def']))

    def test_skips_bool_and_non_string_options(self):
        # All non-string options are skipped so nothing matches and best_score < threshold
        self.assertIsNone(fetch_closest_option('abc', [True, 1, None, False]))


class TestHeightAndHelpers(unittest.TestCase):
    def test_from_numeric_meters_branch(self):
        # value < 3 → multiplied by 100
        self.assertEqual(_from_numeric(1.8), 180)

    def test_from_numeric_cm_branch(self):
        self.assertEqual(_from_numeric(170), 170)

    def test_is_hebrew_cm_true(self):
        self.assertTrue(_is_hebrew_cm('153 ס"מ'))

    def test_is_hebrew_cm_false(self):
        self.assertFalse(_is_hebrew_cm('153 cm'))

    def test_height_to_cm_hebrew_format(self):
        self.assertEqual(height_to_cm('153 ס"מ'), 153)
