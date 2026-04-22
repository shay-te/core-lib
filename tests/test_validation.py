import unittest

from core_lib.helpers.validation import (
    is_bool,
    is_email,
    is_float,
    is_int,
    is_int_enum,
    is_url,
    parse_comma_separated_list,
    parse_int_list,
)
import enum


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class TestIsBool(unittest.TestCase):
    def test_true_string_variants(self):
        self.assertTrue(is_bool("true"))
        self.assertTrue(is_bool("True"))
        self.assertTrue(is_bool("TRUE"))
        self.assertTrue(is_bool("TrUe"))

    def test_false_string_variants(self):
        self.assertTrue(is_bool("false"))
        self.assertTrue(is_bool("False"))
        self.assertTrue(is_bool("FALSE"))
        self.assertTrue(is_bool("FaLsE"))

    def test_bool_literals(self):
        self.assertTrue(is_bool(True))
        self.assertTrue(is_bool(False))

    def test_rejects_non_bool_strings(self):
        self.assertFalse(is_bool("yes"))
        self.assertFalse(is_bool("no"))
        self.assertFalse(is_bool("1"))
        self.assertFalse(is_bool("0"))
        self.assertFalse(is_bool(""))
        self.assertFalse(is_bool("truee"))
        self.assertFalse(is_bool("false "))   # trailing space — not stripped
        self.assertFalse(is_bool(" true"))    # leading space — not stripped
        self.assertFalse(is_bool("  true  ")) # surrounding spaces — not stripped

    def test_rejects_non_bool_types(self):
        self.assertFalse(is_bool(1))      # int 1 is not bool
        self.assertFalse(is_bool(0))      # int 0 is not bool
        self.assertFalse(is_bool(None))
        self.assertFalse(is_bool([]))
        self.assertFalse(is_bool({}))
        self.assertFalse(is_bool(14))


class TestIsFloat(unittest.TestCase):
    def test_float_literals(self):
        self.assertTrue(is_float(0.0))
        self.assertTrue(is_float(1.5))
        self.assertTrue(is_float(-3.14))
        self.assertTrue(is_float(0.0014))

    def test_int_is_float(self):
        self.assertTrue(is_float(0))
        self.assertTrue(is_float(14))
        self.assertTrue(is_float(-7))

    def test_bool_is_float(self):
        # bool is a subclass of int in Python — float(True) == 1.0
        self.assertTrue(is_float(True))
        self.assertTrue(is_float(False))

    def test_numeric_strings(self):
        self.assertTrue(is_float("0.0014"))
        self.assertTrue(is_float("14"))
        self.assertTrue(is_float("-3.14"))
        self.assertTrue(is_float("1e10"))
        self.assertTrue(is_float("1.5e-3"))

    def test_whitespace_numeric_strings(self):
        # float() accepts surrounding whitespace
        self.assertTrue(is_float("  3.14  "))
        self.assertTrue(is_float(" 0 "))

    def test_special_float_strings(self):
        self.assertTrue(is_float("NaN"))
        self.assertTrue(is_float("inf"))
        self.assertTrue(is_float("Infinity"))
        self.assertTrue(is_float("-inf"))

    def test_float_infinity_itself(self):
        self.assertTrue(is_float(float('inf')))
        self.assertTrue(is_float(float('-inf')))
        self.assertTrue(is_float(float('nan')))

    def test_rejects_non_numeric(self):
        self.assertFalse(is_float("strings here"))
        self.assertFalse(is_float("1.2.3"))
        self.assertFalse(is_float("1,000"))   # comma-separated not supported
        self.assertFalse(is_float(""))
        self.assertFalse(is_float("abc"))

    def test_rejects_complex(self):
        self.assertFalse(is_float(1+2j))

    def test_rejects_collections(self):
        self.assertFalse(is_float((1, 2, 3)))
        self.assertFalse(is_float([1, 2, 3]))
        self.assertFalse(is_float({1, 2, 3}))

    def test_rejects_none(self):
        self.assertFalse(is_float(None))


class TestIsInt(unittest.TestCase):
    def test_int_literals(self):
        self.assertTrue(is_int(0))
        self.assertTrue(is_int(14))
        self.assertTrue(is_int(-7))

    def test_int_strings(self):
        self.assertTrue(is_int("14"))
        self.assertTrue(is_int("-5"))
        self.assertTrue(is_int("0"))

    def test_bool_is_int(self):
        # bool is a subclass of int in Python — int(True) == 1
        self.assertTrue(is_int(True))
        self.assertTrue(is_int(False))

    def test_whole_float_is_int(self):
        # int(1.0) == 1 — Python truncates floats to int
        self.assertTrue(is_int(1.0))
        self.assertTrue(is_int(0.0014))  # int(0.0014) == 0

    def test_float_infinity_does_not_crash(self):
        # int(float('inf')) raises OverflowError — must not propagate
        self.assertFalse(is_int(float('inf')))
        self.assertFalse(is_int(float('-inf')))

    def test_float_nan_does_not_crash(self):
        # int(float('nan')) raises ValueError
        self.assertFalse(is_int(float('nan')))

    def test_underscore_separator_string(self):
        # Python int() accepts underscore separators: int("1_000") == 1000
        self.assertTrue(is_int("1_000"))

    def test_rejects_hex_string(self):
        # int("0x10") raises ValueError — only decimal strings accepted
        self.assertFalse(is_int("0x10"))

    def test_rejects_float_strings(self):
        self.assertFalse(is_int("0.5"))
        self.assertFalse(is_int("3.14"))
        self.assertFalse(is_int("1e10"))

    def test_rejects_non_numeric(self):
        self.assertFalse(is_int("NaN"))
        self.assertFalse(is_int("strings here"))
        self.assertFalse(is_int(""))
        self.assertFalse(is_int("1a"))

    def test_rejects_complex(self):
        self.assertFalse(is_int(1+2j))

    def test_rejects_collections(self):
        self.assertFalse(is_int((1, 2, 3)))
        self.assertFalse(is_int([1, 2, 3]))
        self.assertFalse(is_int({1, 2, 3}))

    def test_rejects_none(self):
        self.assertFalse(is_int(None))


class TestIsEmail(unittest.TestCase):
    def test_valid_emails(self):
        self.assertTrue(is_email("abc@xyz.com"))
        self.assertTrue(is_email("abc.def@xyz.com"))
        self.assertTrue(is_email("example.firstname-lastname@email.com"))
        self.assertTrue(is_email("example@email.co.jp"))
        self.assertTrue(is_email("example@email.museum"))
        self.assertTrue(is_email("_______@email.com"))
        self.assertTrue(is_email("example@email-one.com"))
        self.assertTrue(is_email("example+tag@email.com"))
        self.assertTrue(is_email("0987654321@example.com"))
        self.assertTrue(is_email("a@b.io"))
        self.assertTrue(is_email("x@y.cc"))
        self.assertTrue(is_email("valid_email-123@very.long-subdomain.example.com"))

    def test_rejects_malformed(self):
        self.assertFalse(is_email('"email"@example.com'))
        self.assertFalse(is_email("as;fj123.df@asdfa/c.vcom"))
        self.assertFalse(is_email("<asd>>@strange.com"))

    def test_rejects_structural_errors(self):
        self.assertFalse(is_email(".abc@xyz.com"))      # starts with dot
        self.assertFalse(is_email("abc..def@xyz.com"))  # consecutive dots
        self.assertFalse(is_email("abc@-xyz.com"))      # domain starts with hyphen
        self.assertFalse(is_email("abc@.com"))          # domain starts with dot
        self.assertFalse(is_email("abc@xyz.c"))         # single-char TLD
        self.assertFalse(is_email("abc@xyz."))          # ends with dot
        self.assertFalse(is_email("abc@"))              # missing domain
        self.assertFalse(is_email("abc.xyz.com"))       # missing @

    def test_rejects_empty_and_none(self):
        self.assertFalse(is_email(None))
        self.assertFalse(is_email(""))
        self.assertFalse(is_email("   "))


class TestIsUrl(unittest.TestCase):
    def test_valid_urls(self):
        self.assertTrue(is_url("http://domain.com"))  # NOSONAR - intentional test coverage for accepted http URLs
        self.assertTrue(is_url("https://domain.com"))
        self.assertTrue(is_url("https://www.domain.com"))
        self.assertTrue(is_url("https://subdomain.domain.com"))
        self.assertTrue(is_url("http://domain.com.co.uk"))  # NOSONAR - intentional test coverage for accepted http URLs
        self.assertTrue(is_url("https://192.168.1.1"))
        self.assertTrue(is_url("http://localhost"))  # NOSONAR - intentional test coverage for accepted http URLs
        self.assertTrue(is_url("http://localhost:8080"))  # NOSONAR - intentional test coverage for accepted http URLs
        self.assertTrue(is_url("https://domain.com/path/to/page"))
        self.assertTrue(is_url("https://domain.com?query=1&other=2"))
        self.assertTrue(is_url("https://domain.com:443/path"))

    def test_rejects_wrong_scheme(self):
        self.assertFalse(is_url("ftp://domain.com"))
        self.assertFalse(is_url("random://domain.com"))
        self.assertFalse(is_url("telnet://domain.com"))
        self.assertFalse(is_url("ssh://domain.com"))

    def test_rejects_no_scheme(self):
        self.assertFalse(is_url("domain.com"))
        self.assertFalse(is_url("subdomain.domain.com"))
        self.assertFalse(is_url("192.168.0.0"))

    def test_rejects_malformed(self):
        self.assertFalse(is_url("http://"))  # NOSONAR - intentional malformed http fixture
        self.assertFalse(is_url("http://domain"))  # NOSONAR - intentional malformed http fixture with no TLD
        self.assertFalse(is_url("hello world"))
        self.assertFalse(is_url("12345"))

    def test_rejects_empty_and_none(self):
        self.assertFalse(is_url(None))
        self.assertFalse(is_url(""))


class TestIsIntEnum(unittest.TestCase):
    def test_valid_enum_values(self):
        self.assertTrue(is_int_enum(1, MyEnum))
        self.assertTrue(is_int_enum(2, MyEnum))
        self.assertTrue(is_int_enum(3, MyEnum))

    def test_rejects_invalid_values(self):
        self.assertFalse(is_int_enum(0, MyEnum))
        self.assertFalse(is_int_enum(4, MyEnum))
        self.assertFalse(is_int_enum(99, MyEnum))
        self.assertFalse(is_int_enum(-1, MyEnum))

    def test_rejects_none_and_non_enum(self):
        self.assertFalse(is_int_enum(None, MyEnum))
        self.assertFalse(is_int_enum(1, "not_an_enum"))
        self.assertFalse(is_int_enum(1, None))


class TestParseCommaSeparatedList(unittest.TestCase):
    def test_basic_parsing(self):
        self.assertEqual(parse_comma_separated_list("a,b,c"), ["a", "b", "c"])

    def test_strips_whitespace(self):
        self.assertEqual(parse_comma_separated_list("alpha, beta , ,gamma"), ["alpha", "beta", "gamma"])

    def test_ignores_empty_segments(self):
        self.assertEqual(parse_comma_separated_list("a,,b"), ["a", "b"])
        self.assertEqual(parse_comma_separated_list(",a,"), ["a"])

    def test_empty_and_none(self):
        self.assertEqual(parse_comma_separated_list(""), [])
        self.assertEqual(parse_comma_separated_list(None), [])

    def test_single_value(self):
        self.assertEqual(parse_comma_separated_list("only"), ["only"])

    def test_with_value_parser(self):
        self.assertEqual(parse_comma_separated_list("1, 3, 5", value_parser=int), [1, 3, 5])

    def test_value_parser_strips_before_parsing(self):
        self.assertEqual(parse_comma_separated_list("1, 3 ,4,5, ,10", value_parser=int), [1, 3, 4, 5, 10])

    def test_accepts_list_input(self):
        self.assertEqual(parse_comma_separated_list(["a", " b ", "c"]), ["a", "b", "c"])

    def test_parse_int_list(self):
        self.assertEqual(parse_int_list("1, 3 ,4,5, ,10"), [1, 3, 4, 5, 10])
        self.assertEqual(parse_int_list(""), [])
