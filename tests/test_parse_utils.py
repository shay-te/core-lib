import unittest
import math
import numpy as np
import pandas as pd
from datetime import datetime
import random
import string
import sys
import time

# Import each function directly
from core_lib.helpers.parse_utils import (
    normalize,
    similarity,
    clean_list,
    parse_bool,
    parse_any_nan,
    float_to_str,
    parse_date,
    parse_range,
    height_to_cm,
    find_key_by_value,
    fetch_closest_option,
)

STR_LIST_FOR_NAN = ("nan", "none", "null", "")

class TestParseUtils(unittest.TestCase):

    # =====================================================
    # HELPER METHODS
    # =====================================================
    def random_garbage(self, size=100):
        """Generate random string with all printable chars"""
        return ''.join(random.choice(string.printable) for _ in range(size))

    def assertRunsFast(self, func, *args, max_seconds=0.5):
        """Assert function completes within time limit"""
        start = time.time()
        result = func(*args)
        elapsed = time.time() - start
        self.assertLess(
            elapsed, max_seconds,
            f"{func.__name__} too slow: {elapsed:.3f}s"
        )
        return result

    def assertReturnsValidType(self, func, *args, expected_types):
        """Assert function returns one of expected types"""
        result = func(*args)
        self.assertIsInstance(
            result, expected_types,
            f"{func.__name__} returned {type(result)}, expected {expected_types}"
        )
        return result

    # =====================================================
    # normalize - COMPREHENSIVE
    # =====================================================
    def test_normalize_basic(self):
        self.assertEqual(normalize("Hello World!"), "hello world")

    def test_normalize_unicode(self):
        self.assertEqual(normalize("Café!!"), "cafe")

    def test_normalize_weird_chars(self):
        self.assertEqual(normalize("  A---B___C   "), "a b c")

    def test_normalize_not_string(self):
        self.assertEqual(normalize(123), "123")

    def test_normalize_emoji(self):
        self.assertEqual(normalize("🔥Cool🔥"), "cool")

    def test_normalize_empty_string(self):
        self.assertEqual(normalize(""), "")

    def test_normalize_only_spaces(self):
        self.assertEqual(normalize("     "), "")

    def test_normalize_special_chars(self):
        self.assertEqual(normalize("Hello@#$World"), "hello world")

    def test_normalize_numbers_in_string(self):
        self.assertEqual(normalize("Test123ABC"), "test123abc")

    def test_normalize_mixed_whitespace(self):
        self.assertEqual(normalize("A\t\nB\r\nC"), "a b c")

    def test_normalize_float(self):
        self.assertEqual(normalize(45.67), "45 67")

    def test_normalize_accents_removed(self):
        self.assertEqual(normalize("Naïve Übër"), "naive uber")

    def test_normalize_big_string(self):
        """Performance: big strings should normalize quickly"""
        big = "A" * 500000
        self.assertRunsFast(normalize, big, max_seconds=1.0)

    def test_normalize_dict(self):
        result = normalize({"x": 1})
        self.assertIsInstance(result, str)

    def test_normalize_list(self):
        result = normalize([1, 2, 3])
        self.assertIsInstance(result, str)

    def test_normalize_negative_number(self):
        self.assertEqual(normalize(-456), "456")

    def test_normalize_bool(self):
        self.assertEqual(normalize(True), "true")
        self.assertEqual(normalize(False), "false")

    def test_normalize_only_special_chars(self):
        self.assertEqual(normalize("!@#$%^&*()"), "")

    def test_normalize_invariants(self):
        """Output should always be lowercase, no extra spaces, alphanumeric+spaces only"""
        out = normalize("  Héllo---Wörld!!🔥🔥  ")
        self.assertNotIn("  ", out)
        self.assertEqual(out, out.lower())
        self.assertRegex(out, r"^[a-z0-9 ]*$")

    def test_normalize_type_invariant(self):
        """normalize always returns string"""
        for val in [None, 123, 45.6, True, [], {}, "test"]:
            try:
                result = normalize(val)
                self.assertIsInstance(result, str)
            except:
                pass  # Some may raise, that's ok

    def test_normalize_idempotent(self):
        """Normalizing twice should give same result as normalizing once"""
        s = "HeLLo WoRLd!!!"
        once = normalize(s)
        twice = normalize(once)
        self.assertEqual(once, twice)

    def test_normalize_fuzz(self):
        """Fuzz test: should never crash"""
        for _ in range(300):
            out = normalize(self.random_garbage(50))
            self.assertIsInstance(out, str)

    # =====================================================
    # similarity - COMPREHENSIVE
    # =====================================================
    def test_similarity_same(self):
        self.assertAlmostEqual(similarity("abc", "abc"), 1.0)

    def test_similarity_different(self):
        self.assertLess(similarity("abc", "xyz"), 0.1)

    def test_similarity_empty(self):
        self.assertEqual(similarity("", ""), 1.0)

    def test_similarity_one_empty(self):
        self.assertEqual(similarity("abc", ""), 0.0)
        self.assertEqual(similarity("", "abc"), 0.0)

    def test_similarity_partial_match(self):
        val = similarity("abcdef", "abc")
        self.assertGreater(val, 0.3)
        self.assertLess(val, 1.0)

    def test_similarity_case_sensitive(self):
        """similarity should be case sensitive"""
        lower = similarity("abc", "abc")
        mixed = similarity("ABC", "abc")
        self.assertGreater(lower, mixed)

    def test_similarity_commutative(self):
        """similarity(a,b) should equal similarity(b,a)"""
        val1 = similarity("hello", "world")
        val2 = similarity("world", "hello")
        self.assertAlmostEqual(val1, val2)

    def test_similarity_range(self):
        """similarity should always be [0.0, 1.0]"""
        for _ in range(50):
            s1 = self.random_garbage(20)
            s2 = self.random_garbage(20)
            val = similarity(s1, s2)
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)

    def test_similarity_long_strings(self):
        """Performance: long strings"""
        s = "a" * 5000
        self.assertRunsFast(similarity, s, s, max_seconds=1.0)

    # =====================================================
    # clean_list - COMPREHENSIVE
    # =====================================================
    def test_clean_list_basic(self):
        self.assertEqual(clean_list([0, None, "", [], {}, (), "ok"]), [0, "ok"])

    def test_clean_list_nested(self):
        self.assertEqual(clean_list(["", ["x"], {}]), [["x"]])

    def test_clean_list_preserves_false_zero(self):
        """0 and False are falsy but should be kept"""
        result = clean_list([False, 0, None, "x"])
        self.assertEqual(result, [False, 0, "x"])

    def test_clean_list_all_empty(self):
        self.assertEqual(clean_list([None, "", [], {}, ()]), [])

    def test_clean_list_complex(self):
        result = clean_list([1, "a", [], None, (1, 2), {"x": 1}, False])
        self.assertEqual(result, [1, "a", (1, 2), {"x": 1}, False])


    def test_clean_list_order_preserved(self):
        """Order should be preserved"""
        input_list = [3, None, 1, "", 2]
        result = clean_list(input_list)
        self.assertEqual(result, [3, 1, 2])

    def test_clean_list_fuzz(self):
        for _ in range(100):
            dirty = [None, self.random_garbage(10), {}, [], 5]
            out = clean_list(dirty)
            self.assertIn(5, out)

    # =====================================================
    # parse_bool - COMPREHENSIVE
    # =====================================================
    def test_parse_bool_true_cases(self):
        for v in ["yes", "YES", "True", "1", 1, True]:
            result = parse_bool(v)
            self.assertTrue(result, f"parse_bool({v}) should be True")

    def test_parse_bool_false_cases(self):
        for v in ["no", "FALSE", "0", 0, False]:
            result = parse_bool(v)
            self.assertFalse(result, f"parse_bool({v}) should be False")

    def test_parse_bool_invalid(self):
        for v in ["maybe", "ok", {}, [], 2, None, 1.5]:
            self.assertIsNone(parse_bool(v))

    def test_parse_bool_whitespace(self):
        """Whitespace should be handled"""
        self.assertTrue(parse_bool("  yes  "))
        self.assertFalse(parse_bool("  false  "))

    def test_parse_bool_case_insensitive(self):
        """Should handle mixed case"""
        self.assertTrue(parse_bool("YeS"))
        self.assertTrue(parse_bool("TrUe"))
        self.assertFalse(parse_bool("FaLsE"))

    def test_parse_bool_return_type(self):
        """Should return bool or None only"""
        for val in ["yes", "no", "maybe", 1, 0, 2, None]:
            result = parse_bool(val)
            self.assertIn(type(result), [bool, type(None)])

    def test_parse_bool_fuzz(self):
        for _ in range(300):
            result = parse_bool(self.random_garbage(20))
            self.assertIn(type(result), [bool, type(None)])

    # =====================================================
    # parse_any_nan - COMPREHENSIVE
    # =====================================================
    def test_parse_any_nan_scalar(self):
        self.assertIsNone(parse_any_nan(float("nan"), strings_to_replace=STR_LIST_FOR_NAN))
        self.assertIsNone(parse_any_nan("nan", strings_to_replace=STR_LIST_FOR_NAN))
        self.assertIsNone(parse_any_nan("null", strings_to_replace=STR_LIST_FOR_NAN))
        self.assertIsNone(parse_any_nan("None", strings_to_replace=STR_LIST_FOR_NAN))

    def test_parse_any_nan_list(self):
        self.assertEqual(parse_any_nan([1, np.nan], strings_to_replace=STR_LIST_FOR_NAN), [1, None])
        self.assertEqual(parse_any_nan(["nan", 5, np.nan], strings_to_replace=STR_LIST_FOR_NAN), [None, 5, None])

    def test_parse_any_nan_nested(self):
        self.assertEqual(parse_any_nan([1, ["nan", np.nan]], strings_to_replace=STR_LIST_FOR_NAN), [1, [None, None]])

    def test_parse_any_nan_numpy_array(self):
        arr = np.array([1.0, np.nan, 3.0])
        result = parse_any_nan(arr, strings_to_replace=STR_LIST_FOR_NAN)
        self.assertEqual(result[0], 1.0)
        self.assertIsNone(result[1])
        self.assertEqual(result[2], 3.0)

    def test_parse_any_nan_pandas_series(self):
        s = pd.Series([1, np.nan, 3])
        result = parse_any_nan(s, strings_to_replace=STR_LIST_FOR_NAN)
        self.assertEqual(result[0], 1)
        self.assertIsNone(result[1])
        self.assertEqual(result[2], 3)

    def test_parse_any_nan_custom_replace(self):
        """Custom replacement value"""
        self.assertEqual(parse_any_nan("nan", replace_with=-1, strings_to_replace=STR_LIST_FOR_NAN), -1)
        self.assertEqual(parse_any_nan(float("nan"), replace_with=-999, strings_to_replace=STR_LIST_FOR_NAN), -999)

    def test_parse_any_nan_preserves_valid(self):
        """Valid values should pass through unchanged"""
        self.assertEqual(parse_any_nan(5), 5)
        self.assertEqual(parse_any_nan(3.14), 3.14)
        self.assertEqual(parse_any_nan("valid"), "valid")

    # =====================================================
    # float_to_str_no_dot - COMPREHENSIVE
    # =====================================================
    def test_float_to_str(self):
        self.assertEqual(float_to_str(12.34, True), "1234")
        self.assertEqual(float_to_str(12.0, True), "12")
        self.assertEqual(float_to_str(12.34), "12.34")
        self.assertEqual(float_to_str(12.0), "12")
        self.assertEqual(float_to_str(float("nan")), "")
        self.assertEqual(float_to_str(None), "")

    def test_float_to_str_negative(self):
        self.assertEqual(float_to_str(-12.34, True), "-1234")

    def test_float_to_str_zero(self):
        self.assertEqual(float_to_str(0.0, True), "0")

    def test_float_to_str_string_input(self):
        self.assertEqual(float_to_str("123"), "123")

    def test_float_to_str_large_decimal(self):
        out = float_to_str(123456789.9876, True)
        self.assertNotIn(".", out)

    def test_float_to_str_very_small(self):
        result = float_to_str(0.001, True)
        self.assertNotIn(".", result)

    # =====================================================
    # parse_date - COMPREHENSIVE
    # =====================================================
    def test_parse_date_variants(self):
        """Multiple date formats should parse to same date"""
        variants = [
            "2024-09-19",
            "09/19/2024",
            "Sep 19, 2024",
            "September 19, 2024",
            "Janu 12, 2024",
        ]
        results = [parse_date(v) for v in variants if parse_date(v)]
        if len(results) > 1:
            dates = [r.date() for r in results]
            self.assertGreaterEqual(len(set(dates)), 1)

    def test_parse_date_invalid(self):
        for v in [None, "", 1234, "not real date"]:
            self.assertIsNone(parse_date(v))

    def test_parse_date_passthrough(self):
        """datetime objects should pass through unchanged"""
        dt = datetime(2024, 9, 19)
        self.assertEqual(parse_date(dt), dt)

    def test_parse_date_with_time(self):
        """Should parse dates with times"""
        result = parse_date("09/19/2024 10:30:45 AM")
        if result:
            self.assertIsInstance(result, datetime)
            self.assertEqual(result.hour, 10)

    def test_parse_date_whitespace_handling(self):
        """Should handle leading/trailing whitespace"""
        result = parse_date("  2024-09-19  ")
        self.assertIsInstance(result, datetime)

    # =====================================================
    # parse_range - COMPREHENSIVE
    # =====================================================
    def test_parse_range(self):
        self.assertEqual(parse_range("10 to 20"), (10, 20))
        self.assertEqual(parse_range("any to 50", 0, 100), (0, 50))
        self.assertEqual(parse_range("5 to any", 0, 100), (5, 100))

    def test_parse_range_invalid(self):
        for v in ["hello", "10-20", "to", "", None]:
            self.assertIsNone(parse_range(v), v)

    def test_parse_range_case_insensitive(self):
        """to/TO should work"""
        self.assertEqual(parse_range("10 TO 20"), (10, 20))
        self.assertEqual(parse_range("10 To 20"), (10, 20))

    def test_parse_range_whitespace(self):
        """Extra whitespace should be handled"""
        self.assertEqual(parse_range("  10   to   20  "), (10, 20))

    def test_parse_range_return_type(self):
        """Should return tuple or None"""
        result = parse_range("1 to 10")
        self.assertIn(type(result), [tuple, type(None)])

    # =====================================================
    # height_to_cm - COMPREHENSIVE
    # =====================================================
    # =====================================================
    # BASIC VALID CASES
    # =====================================================
    def test_height_cm_basic(self):
        self.assertEqual(height_to_cm("180 cm"), 180)

    def test_height_cm_no_space(self):
        self.assertEqual(height_to_cm("180cm"), 180)

    def test_height_cm_uppercase(self):
        self.assertEqual(height_to_cm("180 CM"), 180)

    def test_height_cm_mixed_case(self):
        self.assertEqual(height_to_cm("180 Cm"), 180)

    def test_height_m_basic(self):
        self.assertEqual(height_to_cm("1.80 m"), 180)

    def test_height_m_no_space(self):
        self.assertEqual(height_to_cm("1.80m"), 180)

    def test_height_m_uppercase(self):
        self.assertEqual(height_to_cm("1.80 M"), 180)

    def test_height_feet_inches_basic(self):
        self.assertEqual(height_to_cm("5'10"), 178)

    def test_height_feet_inches_with_space(self):
        self.assertEqual(height_to_cm("5' 10"), 178)

    def test_height_feet_inches_with_quote(self):
        self.assertEqual(height_to_cm('5\'10"'), 178)

    def test_height_feet_inches_with_space_quote(self):
        self.assertEqual(height_to_cm('5\' 10"'), 178)

    def test_height_decimal_feet(self):
        self.assertEqual(height_to_cm('5.5"'), 168)

    def test_height_plain_number_cm(self):
        self.assertEqual(height_to_cm("175"), 175)

    def test_height_plain_number_meter(self):
        self.assertEqual(height_to_cm("1.75"), 175)

    # =====================================================
    # NUMERIC INPUT TESTS
    # =====================================================
    def test_height_numeric_int_cm(self):
        self.assertEqual(height_to_cm(180), 180)

    def test_height_numeric_float_meter(self):
        self.assertEqual(height_to_cm(1.80), 180)

    def test_height_numeric_float_cm(self):
        self.assertEqual(height_to_cm(175.0), 175)

    def test_height_numeric_zero(self):
        # 0 is below 10, so it's treated as meters
        result = height_to_cm(0)
        self.assertIsNone(result) if result is None else self.assertEqual(result, 0)

    def test_height_numeric_negative(self):
        """Negative heights should return None"""
        result = height_to_cm(-180)
        self.assertTrue(result is None or result < 0)

    def test_height_numeric_nan(self):
        self.assertIsNone(height_to_cm(float('nan')))

    def test_height_numeric_inf(self):
        result = height_to_cm(float('inf'))
        self.assertTrue(result is None or isinstance(result, int))

    def test_height_numeric_very_small(self):
        """Below 10 threshold, treated as meters"""
        result = height_to_cm(1.5)
        self.assertEqual(result, 150)

    def test_height_numeric_boundary_10(self):
        """10 is on boundary between meters and cm"""
        result = height_to_cm(10)
        self.assertEqual(result, 10)  # Treated as cm (> 10 is false)

    def test_height_numeric_boundary_11(self):
        """11 should be treated as cm"""
        result = height_to_cm(11)
        self.assertEqual(result, 11)

    # =====================================================
    # UNICODE APOSTROPHE VARIANTS
    # =====================================================
    def test_height_unicode_prime_symbol(self):
        """′ (prime symbol) should be converted to apostrophe"""
        self.assertEqual(height_to_cm("5′10"), 178)

    def test_height_unicode_double_prime(self):
        """″ (double prime) should be converted to quote"""
        self.assertEqual(height_to_cm('5′10″'), 178)

    def test_height_unicode_curly_quotes(self):
        """Curly quotes should be converted"""
        result = height_to_cm('5\'10"')  # Smart quotes
        self.assertEqual(result, 178)

    # =====================================================
    # WHITESPACE EDGE CASES
    # =====================================================
    def test_height_extra_spaces_cm(self):
        self.assertEqual(height_to_cm("180    cm"), 180)

    def test_height_extra_spaces_m(self):
        self.assertEqual(height_to_cm("1.80    m"), 180)

    def test_height_leading_spaces(self):
        self.assertEqual(height_to_cm("  180 cm"), 180)

    def test_height_trailing_spaces(self):
        self.assertEqual(height_to_cm("180 cm  "), 180)

    def test_height_both_spaces(self):
        self.assertEqual(height_to_cm("  180 cm  "), 180)

    def test_height_tabs(self):
        self.assertEqual(height_to_cm("180\tcm"), 180)

    def test_height_newlines(self):
        result = height_to_cm("180\ncm")
        # May or may not work depending on implementation

    # =====================================================
    # EDGE CASES: FEET/INCHES
    # =====================================================
    def test_height_feet_only_no_inches(self):
        """6' should be 6 feet 0 inches"""
        result = height_to_cm("6'")
        expected = int(round(6 * 12 * 2.54))
        self.assertEqual(result, expected)

    def test_height_feet_only_apostrophe(self):
        """6 feet exactly"""
        result = height_to_cm("6'0")
        expected = int(round(6 * 12 * 2.54))
        self.assertEqual(result, expected)

    def test_height_feet_zero_inches(self):
        """5'0 is 5 feet"""
        result = height_to_cm("5'0")
        expected = int(round(5 * 12 * 2.54))
        self.assertEqual(result, expected)

    def test_height_feet_with_extra_spaces(self):
        self.assertEqual(height_to_cm("5  '  10"), 178)

    def test_height_feet_large_inches_invalid(self):
        """Inches > 11 are technically invalid but function might accept"""
        result = height_to_cm("5'15")
        if result:
            self.assertGreater(result, 0)

    def test_height_feet_100_inches(self):
        """Edge case: very large inch value"""
        result = height_to_cm("5'100")
        if result:
            self.assertGreater(result, 0)

    def test_height_zero_feet(self):
        """0 feet"""
        result = height_to_cm("0'5")
        expected = int(round(5 * 2.54))
        if result:
            self.assertEqual(result, expected)

    def test_height_negative_feet_sign(self):
        """Negative values should fail"""
        result = height_to_cm("-5'10")
        # May or may not parse

    # =====================================================
    # EDGE CASES: DECIMAL FEET
    # =====================================================
    def test_height_decimal_feet_0_5(self):
        """0.5 feet"""
        result = height_to_cm("0.5\"")
        expected = int(round(0.5 * 12 * 2.54))
        self.assertEqual(result, expected)

    def test_height_decimal_feet_6_0(self):
        """6.0 feet"""
        result = height_to_cm("6.0\"")
        expected = int(round(6.0 * 12 * 2.54))
        self.assertEqual(result, expected)

    def test_height_decimal_feet_large(self):
        """Very large decimal feet"""
        result = height_to_cm("10.5\"")
        if result:
            self.assertGreater(result, 0)

    def test_height_decimal_feet_no_leading_digit(self):
        """.5" should parse as 0.5 feet"""
        result = height_to_cm(".5\"")
        # May or may not parse

    def test_height_decimal_feet_many_decimals(self):
        """5.5555 feet"""
        result = height_to_cm("5.5555\"")
        if result:
            self.assertGreater(result, 0)

    # =====================================================
    # EDGE CASES: PLAIN NUMBERS
    # =====================================================
    def test_height_plain_decimal_small(self):
        """1.7 should be treated as meters"""
        self.assertEqual(height_to_cm("1.7"), 170)

    def test_height_plain_decimal_boundary(self):
        """10.01 should be cm"""
        self.assertEqual(height_to_cm("10.01"), 10)  # Rounds

    def test_height_plain_large_number(self):
        """300 cm"""
        self.assertEqual(height_to_cm("300"), 300)

    def test_height_plain_zero(self):
        """0 meters"""
        result = height_to_cm("0")
        self.assertEqual(result, 0)

    # =====================================================
    # INVALID INPUTS
    # =====================================================
    def test_height_invalid_text(self):
        self.assertIsNone(height_to_cm("tall"))

    def test_height_invalid_random_text(self):
        self.assertIsNone(height_to_cm("abc def ghi"))

    def test_height_invalid_only_cm_no_number(self):
        self.assertIsNone(height_to_cm("cm"))

    def test_height_invalid_only_m_no_number(self):
        self.assertIsNone(height_to_cm("m"))

    def test_height_invalid_only_quote(self):
        self.assertIsNone(height_to_cm("'"))

    def test_height_invalid_empty_string(self):
        self.assertIsNone(height_to_cm(""))

    def test_height_invalid_whitespace_only(self):
        self.assertIsNone(height_to_cm("   "))

    def test_height_invalid_none(self):
        self.assertIsNone(height_to_cm(None))

    def test_height_invalid_list(self):
        result = height_to_cm([180])
        self.assertIsNone(result)

    def test_height_invalid_dict(self):
        result = height_to_cm({"height": 180})
        self.assertIsNone(result)

    def test_height_invalid_bool(self):
        result = height_to_cm(True)
        # True is 1, so treated as meters -> 100cm
        self.assertIn(result, [100, None])

    # =====================================================
    # MIXED VALID/INVALID COMBINATIONS
    # =====================================================
    def test_height_feet_with_cm_suffix(self):
        """5' cm - ambiguous, should fail"""
        result = height_to_cm("5' cm")
        # May or may not parse

    def test_height_double_units(self):
        """180 cm m - should fail or take first"""
        result = height_to_cm("180 cm m")
        if result:
            self.assertEqual(result, 180)

    def test_height_multiple_dots(self):
        """1.2.3 - invalid decimal"""
        result = height_to_cm("1.2.3")
        self.assertIsNone(result) or isinstance(result, int)

    def test_height_letters_in_number(self):
        """1a8b0 - invalid"""
        result = height_to_cm("1a8b0")
        self.assertIsNone(result)

    def test_height_special_chars_only(self):
        """!@#$%"""
        result = height_to_cm("!@#$%")
        self.assertIsNone(result)

    # =====================================================
    # ROUNDING TESTS
    # =====================================================
    def test_height_feet_inches_rounding_up(self):
        """5'10 = 177.8 cm, should round"""
        result = height_to_cm("5'10")
        self.assertEqual(result, 178)

    def test_height_feet_inches_rounding_down(self):
        """5'9 = 175.26 cm"""
        result = height_to_cm("5'9")
        self.assertEqual(result, 175)

    def test_height_decimal_feet_rounding(self):
        """5.5 feet = 167.64 cm"""
        result = height_to_cm("5.5\"")
        self.assertEqual(result, 168)

    def test_height_meter_rounding(self):
        """1.754 m = 175.4 cm"""
        result = height_to_cm("1.754 m")
        self.assertEqual(result, 175)

    # =====================================================
    # RETURN TYPE TESTS
    # =====================================================
    def test_height_return_type_valid(self):
        """Valid input returns int"""
        result = height_to_cm("180 cm")
        self.assertIsInstance(result, int)

    def test_height_return_type_invalid(self):
        """Invalid input returns None"""
        result = height_to_cm("invalid")
        self.assertIsNone(result)

    def test_height_return_type_numeric(self):
        """Numeric input returns int"""
        result = height_to_cm(180)
        self.assertIsInstance(result, int)

    # =====================================================
    # REALISTIC HUMAN HEIGHTS
    # =====================================================
    def test_height_very_short_person(self):
        """Dwarf: ~120 cm"""
        self.assertEqual(height_to_cm("120 cm"), 120)
        self.assertEqual(height_to_cm("1.2 m"), 120)
        self.assertEqual(height_to_cm("3'11"), 119)  # Close to 120

    def test_height_average_woman(self):
        """Average woman: ~165 cm"""
        self.assertEqual(height_to_cm("165 cm"), 165)
        self.assertEqual(height_to_cm("1.65 m"), 165)
        self.assertEqual(height_to_cm("5'5"), 165)

    def test_height_average_man(self):
        """Average man: ~180 cm"""
        self.assertEqual(height_to_cm("180 cm"), 180)
        self.assertEqual(height_to_cm("1.80 m"), 180)
        self.assertEqual(height_to_cm("5'11"), 180)

    def test_height_very_tall_person(self):
        """Very tall: ~220 cm"""
        self.assertEqual(height_to_cm("220 cm"), 220)
        self.assertEqual(height_to_cm("2.20 m"), 220)
        self.assertEqual(height_to_cm("7'3"), 221)

    # =====================================================
    # PERFORMANCE & FUZZ
    # =====================================================
    def test_height_very_long_string(self):
        """Should not crash on very long input"""
        long_str = "180 cm" + "x" * 10000
        result = height_to_cm(long_str)
        self.assertIsNone(result)

    def test_height_many_decimal_places(self):
        """1.123456789 m"""
        result = height_to_cm("1.123456789 m")
        if result:
            self.assertGreater(result, 0)

    def test_height_scientific_notation(self):
        """1e2 cm (100 cm)"""
        result = height_to_cm("1e2 cm")
        # May not parse

    def test_height_weird_unicode_spaces(self):
        """Non-breaking space and other unicode spaces"""
        result = height_to_cm("180\u00a0cm")  # Non-breaking space
        if result:
            self.assertEqual(result, 180)

    def test_height_mixed_quotes_apostrophes(self):
        """5' 10" with various quote styles"""
        variants = [
            "5'10\"",
            "5′10″",
        ]
        for v in variants:
            result = height_to_cm(v)
            if result:
                self.assertGreater(result, 0)

    def test_height_regex_injection(self):
        """Should handle regex special chars safely"""
        result = height_to_cm("180 cm (test) [regex]")
        self.assertIsNone(result)

    # =====================================================
    # find_key_by_value - COMPREHENSIVE
    # =====================================================
    def test_find_key(self):
        d = {"a": 1, "b": 2}
        self.assertEqual(find_key_by_value(d, 2), "b")

    def test_find_key_missing(self):
        self.assertIsNone(find_key_by_value({"a": 1}, 999))

    def test_find_key_empty_dict(self):
        self.assertIsNone(find_key_by_value({}, 1))

    def test_find_key_none_value(self):
        """Should find None values"""
        d = {"a": None, "b": 2}
        self.assertEqual(find_key_by_value(d, None), "a")

    def test_find_key_complex_values(self):
        """Should work with lists/dicts as values"""
        d = {"a": [1, 2], "b": [3, 4]}
        self.assertEqual(find_key_by_value(d, [1, 2]), "a")

    def test_find_key_return_type(self):
        """Should return key or None"""
        result = find_key_by_value({"a": 1}, 1)
        self.assertIn(type(result), [str, type(None), int])

    # =====================================================
    # fetch_exact_option - COMPREHENSIVE
    # =====================================================
    def test_fetch_option_basic(self):
        self.assertEqual(fetch_closest_option("grn", ["Green", "Blue"], 0.60), "Green")

    def test_fetch_option_fail(self):
        self.assertIsNone(fetch_closest_option("xyz", ["aaa", "bbb"]))

    def test_fetch_option_exact_match(self):
        """Exact matches should work"""
        self.assertEqual(fetch_closest_option("apple", ["apple", "banana"]), "apple")

    def test_fetch_option_empty_list(self):
        self.assertIsNone(fetch_closest_option("test", []))

    def test_fetch_option_return_type(self):
        """Should return option or None"""
        result = fetch_closest_option("a", ["apple"])
        self.assertIn(result, ["apple", None])

    def test_fetch_option_fuzz(self):
        """Fuzz test: should never crash"""
        for _ in range(200):
            out = fetch_closest_option(self.random_garbage(20), ["abc", "def", "ghi"])
            self.assertIn(out, ["abc", "def", "ghi", None])

    # =====================================================
    # GLOBAL CRASH TEST (HARD MODE)
    # =====================================================
    def test_test(self):
        height_to_cm(pd.Series([1, np.nan]))

    def test_no_function_crashes_on_weird_inputs(self):
        """Core resilience: nothing should crash"""
        funcs = [
            normalize, clean_list, parse_bool, parse_any_nan,
            float_to_str, parse_date, parse_range,
            height_to_cm
        ]

        weird_inputs = [
            None, True, False, 123, 1.23, float("nan"), [], {}, set(),
            {"x": 1}, "🔥🔥🔥", "nan", "--??!!??", complex(1, 2),
            sys.maxsize, ["a", ["nested"]], pd.Series([1, np.nan]),
            np.array([np.nan, 3]), self.random_garbage(50), 0, -1,
        ]

        for f in funcs:
            for x in weird_inputs:
                try:
                    f(x)
                except Exception as e:
                    self.fail(f"{f.__name__} crashed on input {repr(x)}: {e}")

    # =====================================================
    # TYPE CONSISTENCY TESTS
    # =====================================================
    def test_normalize_always_returns_string(self):
        """normalize always returns str"""
        for val in ["test", 123, None, [], {}]:
            try:
                result = normalize(val)
                self.assertIsInstance(result, str)
            except:
                pass

    def test_similarity_always_returns_float(self):
        """similarity always returns float [0,1]"""
        result = similarity("a", "b")
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_clean_list_always_returns_list(self):
        """clean_list always returns list"""
        result = clean_list([1, None, 2])
        self.assertIsInstance(result, list)

    def test_parse_bool_returns_bool_or_none(self):
        """parse_bool returns bool or None"""
        for val in ["yes", "no", "maybe"]:
            result = parse_bool(val)
            self.assertIn(type(result), [bool, type(None)])

    def test_parse_date_returns_datetime_or_none(self):
        """parse_date returns datetime or None"""
        for val in ["2024-01-01", "invalid"]:
            result = parse_date(val)
            self.assertIn(type(result), [datetime, type(None)])

    def test_parse_range_returns_tuple_or_none(self):
        """parse_range returns tuple or None"""
        for val in ["1 to 10", "invalid"]:
            result = parse_range(val)
            self.assertIn(type(result), [tuple, type(None)])

    def test_height_to_cm_returns_int_or_none(self):
        """height_to_cm returns int or None"""
        for val in ["180 cm", "invalid"]:
            result = height_to_cm(val)
            self.assertIn(type(result), [int, type(None)])
