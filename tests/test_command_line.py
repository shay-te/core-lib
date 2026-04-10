import enum
import unittest
from unittest.mock import patch

from core_lib.helpers import shell_utils
from core_lib.helpers.shell_utils import (
    prompt_bool,
    prompt_comma_list,
    prompt_enum,
    prompt_int,
    prompt_list,
    prompt_options,
    prompt_str,
    prompt_yes_no,
)


class DemoEnum(enum.Enum):
    first = 1
    second = 2
    third = 3


# ── prompt_string ─────────────────────────────────────────────────────────────

class TestPromptString(unittest.TestCase):
    def test_returns_value_immediately(self):
        with patch("builtins.input", return_value="hello"):
            self.assertEqual(shell_utils.prompt_string("Name: "), "hello")

    def test_retries_on_empty_until_non_empty(self):
        with patch("builtins.input", side_effect=["", "  ", "value"]):
            self.assertEqual(shell_utils.prompt_string("Name: "), "value")

    def test_strips_whitespace(self):
        with patch("builtins.input", return_value="  hello  "):
            self.assertEqual(shell_utils.prompt_string("Name: "), "hello")

    def test_whitespace_only_counts_as_empty(self):
        # "   ".strip() == "" — treated as empty, retries
        with patch("builtins.input", side_effect=["   ", "\t", "ok"]):
            self.assertEqual(shell_utils.prompt_string("Name: "), "ok")


# ── prompt_str ────────────────────────────────────────────────────────────────

class TestPromptStr(unittest.TestCase):
    def test_returns_typed_value(self):
        with patch("builtins.input", return_value="hello"):
            self.assertEqual(prompt_str("Name"), "hello")

    def test_returns_default_on_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(prompt_str("Name", default="core-lib"), "core-lib")

    def test_retries_when_no_default_and_empty(self):
        with patch("builtins.input", side_effect=["", "", "value"]):
            self.assertEqual(prompt_str("Name"), "value")

    def test_allow_empty_returns_empty_string(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(prompt_str("Optional", allow_empty=True), "")

    def test_allow_none_returns_none_on_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertIsNone(prompt_str("Optional", allow_none=True))

    def test_allow_none_takes_precedence_over_allow_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertIsNone(prompt_str("Optional", allow_empty=True, allow_none=True))

    def test_validate_callback_retries_on_failure(self):
        calls = []
        def reject_first(v):
            calls.append(v)
            return len(calls) > 1
        with patch("builtins.input", side_effect=["bad", "good"]):
            self.assertEqual(prompt_str("Name", validate_callback=reject_first), "good")

    def test_validate_callback_passes_on_success(self):
        with patch("builtins.input", return_value="valid"):
            self.assertEqual(prompt_str("Name", validate_callback=lambda v: v == "valid"), "valid")

    def test_validate_callback_never_called_when_empty_uses_default(self):
        called = []
        with patch("builtins.input", return_value=""):
            result = prompt_str("Name", default="default", validate_callback=lambda v: called.append(v) or True)
        self.assertEqual(result, "default")
        self.assertEqual(called, [])

    def test_typed_value_overrides_default(self):
        with patch("builtins.input", return_value="typed"):
            self.assertEqual(prompt_str("Name", default="default"), "typed")

    def test_strips_whitespace(self):
        with patch("builtins.input", return_value="  hello  "):
            self.assertEqual(prompt_str("Name"), "hello")

    def test_whitespace_only_treated_as_empty(self):
        # "   ".strip() == "" — same as pressing enter
        with patch("builtins.input", side_effect=["   ", "real"]):
            self.assertEqual(prompt_str("Name"), "real")

    def test_validate_callback_receives_stripped_value(self):
        received = []
        with patch("builtins.input", return_value="  hello  "):
            prompt_str("Name", validate_callback=lambda v: received.append(v) or True)
        self.assertEqual(received, ["hello"])

    def test_validate_callback_called_on_each_retry(self):
        attempts = []
        def track(v):
            attempts.append(v)
            return len(attempts) >= 3  # accept on 3rd try
        with patch("builtins.input", side_effect=["a", "b", "c"]):
            result = prompt_str("Name", validate_callback=track)
        self.assertEqual(result, "c")
        self.assertEqual(attempts, ["a", "b", "c"])

    def test_validate_callback_not_called_on_empty_with_allow_none(self):
        called = []
        with patch("builtins.input", return_value=""):
            result = prompt_str("Name", allow_none=True, validate_callback=lambda v: called.append(v) or True)
        self.assertIsNone(result)
        self.assertEqual(called, [])

    def test_default_none_with_allow_empty_returns_empty_not_none(self):
        # allow_empty wins when default is None and allow_none is False
        with patch("builtins.input", return_value=""):
            self.assertEqual(prompt_str("Name", allow_empty=True), "")


# ── prompt_yes_no ─────────────────────────────────────────────────────────────

class TestPromptYesNo(unittest.TestCase):
    def test_yes_variants(self):
        for answer in ("y", "Y", "yes", "YES", "Yes"):
            with patch("builtins.input", return_value=answer):
                self.assertTrue(prompt_yes_no("Continue", default=False))

    def test_no_variants(self):
        for answer in ("n", "N", "no", "NO", "No"):
            with patch("builtins.input", return_value=answer):
                self.assertFalse(prompt_yes_no("Continue", default=True))

    def test_empty_uses_true_default(self):
        with patch("builtins.input", return_value=""):
            self.assertTrue(prompt_yes_no("Continue", default=True))

    def test_empty_uses_false_default(self):
        with patch("builtins.input", return_value=""):
            self.assertFalse(prompt_yes_no("Continue", default=False))

    def test_retries_on_invalid_input(self):
        with patch("builtins.input", side_effect=["maybe", "nope", "y"]):
            self.assertTrue(prompt_yes_no("Continue"))

    def test_retries_when_no_default_and_empty(self):
        with patch("builtins.input", side_effect=["", "n"]):
            self.assertFalse(prompt_yes_no("Continue", default=None))

    def test_rejects_true_false_strings(self):
        # "true"/"false" are not valid — only "y/yes/n/no"
        with patch("builtins.input", side_effect=["true", "false", "y"]):
            self.assertTrue(prompt_yes_no("Continue"))

    def test_rejects_numeric_input(self):
        with patch("builtins.input", side_effect=["1", "0", "n"]):
            self.assertFalse(prompt_yes_no("Continue"))

    def test_whitespace_with_valid_answer(self):
        # _prompt strips — "  yes  " becomes "yes"
        with patch("builtins.input", return_value="  yes  "):
            self.assertTrue(prompt_yes_no("Continue", default=False))

    def test_partial_word_rejected(self):
        with patch("builtins.input", side_effect=["ye", "yess", "yes"]):
            self.assertTrue(prompt_yes_no("Continue"))


# ── prompt_bool ───────────────────────────────────────────────────────────────

class TestPromptBool(unittest.TestCase):
    def test_true_string_variants(self):
        for answer in ("true", "True", "TRUE", "1"):
            with patch("builtins.input", return_value=answer):
                self.assertTrue(prompt_bool("Flag"))

    def test_false_string_variants(self):
        for answer in ("false", "False", "FALSE", "0"):
            with patch("builtins.input", return_value=answer):
                self.assertFalse(prompt_bool("Flag"))

    def test_default_true_on_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertTrue(prompt_bool("Flag", default=True))

    def test_default_false_on_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertFalse(prompt_bool("Flag", default=False))

    def test_allow_none_returns_none_on_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertIsNone(prompt_bool("Flag", allow_none=True))

    def test_retries_on_invalid_input(self):
        with patch("builtins.input", side_effect=["yes", "maybe", "true"]):
            self.assertTrue(prompt_bool("Flag"))

    def test_rejects_yes_no_strings(self):
        # "yes"/"no" are not valid — only "true/false/1/0"
        with patch("builtins.input", side_effect=["yes", "no", "1"]):
            self.assertTrue(prompt_bool("Flag"))

    def test_whitespace_stripped_before_check(self):
        with patch("builtins.input", return_value="  true  "):
            self.assertTrue(prompt_bool("Flag"))

    def test_bool_default_true_resolves_correctly(self):
        with patch("builtins.input", return_value=""):
            self.assertIs(prompt_bool("Flag", default=True), True)

    def test_bool_default_false_resolves_correctly(self):
        with patch("builtins.input", return_value=""):
            self.assertIs(prompt_bool("Flag", default=False), False)


# ── prompt_int ────────────────────────────────────────────────────────────────

class TestPromptInt(unittest.TestCase):
    def test_returns_integer(self):
        with patch("builtins.input", return_value="42"):
            self.assertEqual(prompt_int("Count"), 42)

    def test_returns_negative_integer(self):
        with patch("builtins.input", return_value="-5"):
            self.assertEqual(prompt_int("Count"), -5)

    def test_returns_zero(self):
        with patch("builtins.input", return_value="0"):
            self.assertEqual(prompt_int("Count"), 0)

    def test_returns_default_on_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(prompt_int("Count", default=10), 10)

    def test_returns_zero_default(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(prompt_int("Count", default=0), 0)

    def test_allow_none_returns_none_on_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertIsNone(prompt_int("Count", allow_none=True))

    def test_retries_on_float_string(self):
        with patch("builtins.input", side_effect=["3.14", "7"]):
            self.assertEqual(prompt_int("Count"), 7)

    def test_retries_on_non_numeric(self):
        with patch("builtins.input", side_effect=["abc", "nope", "3"]):
            self.assertEqual(prompt_int("Count"), 3)

    def test_typed_value_overrides_default(self):
        with patch("builtins.input", return_value="99"):
            self.assertEqual(prompt_int("Count", default=1), 99)

    def test_rejects_hex_string(self):
        with patch("builtins.input", side_effect=["0x10", "16"]):
            self.assertEqual(prompt_int("Count"), 16)

    def test_rejects_float_with_decimal(self):
        with patch("builtins.input", side_effect=["3.14", "3"]):
            self.assertEqual(prompt_int("Count"), 3)

    def test_rejects_whitespace_only(self):
        with patch("builtins.input", side_effect=["   ", "5"]):
            self.assertEqual(prompt_int("Count"), 5)

    def test_very_large_number(self):
        with patch("builtins.input", return_value="999999999999999999999"):
            self.assertEqual(prompt_int("Count"), 999999999999999999999)


# ── prompt_enum ───────────────────────────────────────────────────────────────

class TestPromptEnum(unittest.TestCase):
    def test_valid_selection(self):
        with patch("builtins.input", return_value="1"), patch("builtins.print"):
            self.assertEqual(prompt_enum(DemoEnum, "Pick"), 1)

    def test_all_valid_values(self):
        for val in (1, 2, 3):
            with patch("builtins.input", return_value=str(val)), patch("builtins.print"):
                self.assertEqual(prompt_enum(DemoEnum, "Pick"), val)

    def test_default_on_empty(self):
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            self.assertEqual(prompt_enum(DemoEnum, "Pick", default=2), 2)

    def test_retries_on_invalid_number(self):
        with patch("builtins.input", side_effect=["99", "0", "2"]), patch("builtins.print"):
            self.assertEqual(prompt_enum(DemoEnum, "Pick"), 2)

    def test_retries_on_non_numeric(self):
        with patch("builtins.input", side_effect=["abc", "3"]), patch("builtins.print"):
            self.assertEqual(prompt_enum(DemoEnum, "Pick"), 3)

    def test_rejects_float_input(self):
        with patch("builtins.input", side_effect=["1.5", "2"]), patch("builtins.print"):
            self.assertEqual(prompt_enum(DemoEnum, "Pick"), 2)

    def test_rejects_negative_value(self):
        with patch("builtins.input", side_effect=["-1", "1"]), patch("builtins.print"):
            self.assertEqual(prompt_enum(DemoEnum, "Pick"), 1)


# ── prompt_options ────────────────────────────────────────────────────────────

class TestPromptOptions(unittest.TestCase):
    def test_valid_selection(self):
        with patch("builtins.input", return_value="2"), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", ["a", "b", "c"]), "b")

    def test_first_and_last(self):
        with patch("builtins.input", return_value="1"), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", ["x", "y", "z"]), "x")
        with patch("builtins.input", return_value="3"), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", ["x", "y", "z"]), "z")

    def test_default_on_empty(self):
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", ["a", "b"], default="a"), "a")

    def test_retries_on_out_of_range(self):
        with patch("builtins.input", side_effect=["0", "99", "1"]), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", ["a", "b"]), "a")

    def test_retries_on_non_numeric(self):
        with patch("builtins.input", side_effect=["abc", "2"]), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", ["a", "b"]), "b")

    def test_works_with_enum_values(self):
        with patch("builtins.input", return_value="1"), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", list(DemoEnum)), DemoEnum.first)

    def test_raises_on_empty_options(self):
        with self.assertRaises(ValueError):
            prompt_options("Pick", [])

    def test_raises_when_default_not_in_options(self):
        with self.assertRaises(ValueError):
            prompt_options("Pick", ["a", "b"], default="z")

    def test_negative_index_rejected(self):
        with patch("builtins.input", side_effect=["-1", "1"]), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", ["a", "b"]), "a")

    def test_zero_index_rejected(self):
        # list is 1-based
        with patch("builtins.input", side_effect=["0", "1"]), patch("builtins.print"):
            self.assertEqual(prompt_options("Pick", ["a", "b"]), "a")


# ── prompt_list ───────────────────────────────────────────────────────────────

class TestPromptList(unittest.TestCase):
    def test_returns_zero_based_index(self):
        with patch("builtins.input", return_value="1"), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b", "c"], "Pick"), 0)
        with patch("builtins.input", return_value="3"), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b", "c"], "Pick"), 2)

    def test_retries_on_out_of_range(self):
        with patch("builtins.input", side_effect=["0", "99", "2"]), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b", "c"], "Pick"), 1)

    def test_retries_on_non_numeric(self):
        with patch("builtins.input", side_effect=["abc", "1"]), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b"], "Pick"), 0)

    def test_validate_callback_rejects_duplicate(self):
        rejected = set()
        def no_duplicates(val):
            if val in rejected:
                return False
            rejected.add(val)
            return True
        # first pick "a" (idx 0), then try "a" again (rejected), then pick "b" (idx 1)
        with patch("builtins.input", side_effect=["1", "1", "2"]), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b"], "Pick", validate_callback=no_duplicates), 0)
            self.assertEqual(prompt_list(["a", "b"], "Pick", validate_callback=no_duplicates), 1)

    def test_default_used_on_empty(self):
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b", "c"], "Pick", default=2), 1)

    def test_zero_index_rejected(self):
        # 1-based, so 0 is invalid
        with patch("builtins.input", side_effect=["0", "1"]), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b"], "Pick"), 0)

    def test_beyond_length_rejected(self):
        with patch("builtins.input", side_effect=["99", "2"]), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b"], "Pick"), 1)

    def test_negative_index_rejected(self):
        with patch("builtins.input", side_effect=["-1", "1"]), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b"], "Pick"), 0)

    def test_validate_callback_shows_fail_message_then_retries(self):
        reject_count = [0]
        def reject_once(val):
            reject_count[0] += 1
            return reject_count[0] > 1
        with patch("builtins.input", side_effect=["1", "1"]), patch("builtins.print"):
            self.assertEqual(prompt_list(["a", "b"], "Pick", validate_callback=reject_once), 0)


# ── prompt_comma_list ─────────────────────────────────────────────────────────

class TestPromptCommaList(unittest.TestCase):
    def test_basic_parsing(self):
        with patch("builtins.input", return_value="a, b, c"):
            self.assertEqual(prompt_comma_list("Values"), ["a", "b", "c"])

    def test_returns_empty_list_on_empty_input(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(prompt_comma_list("Values"), [])

    def test_returns_default_on_empty_input(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(prompt_comma_list("Values", default=["x", "y"]), ["x", "y"])

    def test_default_is_not_mutated(self):
        default = ["x"]
        with patch("builtins.input", return_value=""):
            result = prompt_comma_list("Values", default=default)
        result.append("mutated")
        self.assertEqual(default, ["x"])

    def test_ignores_empty_segments(self):
        with patch("builtins.input", return_value="a,,b, ,c"):
            self.assertEqual(prompt_comma_list("Values"), ["a", "b", "c"])

    def test_with_int_parser(self):
        with patch("builtins.input", return_value="1, 3 ,4,5, ,10"):
            self.assertEqual(prompt_comma_list("Values", value_parser=int), [1, 3, 4, 5, 10])

    def test_retries_when_parser_raises(self):
        with patch("builtins.input", side_effect=["not,valid,ints", "1,2,3"]):
            self.assertEqual(prompt_comma_list("Values", value_parser=int), [1, 2, 3])

    def test_allow_empty_false_retries_on_empty_result(self):
        with patch("builtins.input", side_effect=["", "a,b"]):
            self.assertEqual(prompt_comma_list("Values", allow_empty=False), ["a", "b"])

    def test_only_commas_returns_empty(self):
        with patch("builtins.input", return_value=",,,"):
            self.assertEqual(prompt_comma_list("Values"), [])

    def test_single_item_no_comma(self):
        with patch("builtins.input", return_value="hello"):
            self.assertEqual(prompt_comma_list("Values"), ["hello"])

    def test_parser_error_retries_entire_input(self):
        # "1,two,3" — "two" makes int() raise, entire input retried
        with patch("builtins.input", side_effect=["1,two,3", "1,2,3"]):
            self.assertEqual(prompt_comma_list("Values", value_parser=int), [1, 2, 3])

    def test_default_is_returned_as_copy_not_reference(self):
        original = ["x", "y"]
        with patch("builtins.input", return_value=""):
            result = prompt_comma_list("Values", default=original)
        result.append("z")
        self.assertEqual(original, ["x", "y"])  # original unmodified

    def test_whitespace_only_input_treated_as_empty(self):
        with patch("builtins.input", side_effect=["   ", "a,b"]):
            self.assertEqual(prompt_comma_list("Values", allow_empty=False), ["a", "b"])
