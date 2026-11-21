import enum
import unittest
from unittest.mock import patch

from core_lib.helpers import shell_utils
from core_lib.helpers.shell_utils import (
    _parse_toggle_indices,
    prompt_bool,
    prompt_comma_list,
    prompt_enum,
    prompt_int,
    prompt_list,
    prompt_multi_select,
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


# ── _parse_toggle_indices ─────────────────────────────────────────────────────

class TestParseToggleIndices(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(_parse_toggle_indices("", 5), [])

    def test_whitespace_only(self):
        self.assertEqual(_parse_toggle_indices("   ", 5), [])

    def test_single_index_one_based_to_zero_based(self):
        self.assertEqual(_parse_toggle_indices("1", 5), [0])
        self.assertEqual(_parse_toggle_indices("5", 5), [4])

    def test_comma_separated(self):
        self.assertEqual(_parse_toggle_indices("1,3,5", 5), [0, 2, 4])

    def test_space_separated(self):
        self.assertEqual(_parse_toggle_indices("1 3 5", 5), [0, 2, 4])

    def test_mixed_commas_and_spaces(self):
        self.assertEqual(_parse_toggle_indices("1, 3 5", 5), [0, 2, 4])

    def test_range_inclusive(self):
        self.assertEqual(_parse_toggle_indices("1-3", 5), [0, 1, 2])

    def test_mixed_range_and_singles(self):
        self.assertEqual(_parse_toggle_indices("1-3,7", 10), [0, 1, 2, 6])

    def test_reversed_range_normalises(self):
        # "3-1" should still yield 1..3 — order in input shouldn't matter
        self.assertEqual(_parse_toggle_indices("3-1", 5), [0, 1, 2])

    def test_single_element_range(self):
        self.assertEqual(_parse_toggle_indices("2-2", 5), [1])

    def test_out_of_range_single_dropped(self):
        self.assertEqual(_parse_toggle_indices("99", 3), [])

    def test_out_of_range_range_partially_clamped(self):
        # "1-5" with max=3 should yield 1,2,3 (not error)
        self.assertEqual(_parse_toggle_indices("1-5", 3), [0, 1, 2])

    def test_range_starting_above_max_drops(self):
        self.assertEqual(_parse_toggle_indices("8-10", 5), [])

    def test_non_numeric_token_dropped(self):
        self.assertEqual(_parse_toggle_indices("abc, 1", 5), [0])

    def test_non_numeric_in_range_dropped(self):
        self.assertEqual(_parse_toggle_indices("a-b", 5), [])
        self.assertEqual(_parse_toggle_indices("1-abc", 5), [])
        self.assertEqual(_parse_toggle_indices("abc-3", 5), [])

    def test_zero_rejected(self):
        # 1-based input — 0 is invalid
        self.assertEqual(_parse_toggle_indices("0", 5), [])

    def test_negative_single_rejected(self):
        # int("-5") parses but fails the 1<=n<=max check
        self.assertEqual(_parse_toggle_indices("-5", 5), [])

    def test_range_with_zero_clamps(self):
        # "0-2" — zero clamped out, 1 and 2 kept
        self.assertEqual(_parse_toggle_indices("0-2", 5), [0, 1])

    def test_max_index_zero_drops_everything(self):
        # empty items list — all input is invalid
        self.assertEqual(_parse_toggle_indices("1,2,3", 0), [])

    def test_duplicates_preserved(self):
        # toggle semantics rely on this — "1,1" toggles twice (no-op)
        self.assertEqual(_parse_toggle_indices("1,1", 5), [0, 0])

    def test_preserves_input_order(self):
        # order matters when the consumer applies XOR semantics
        self.assertEqual(_parse_toggle_indices("3,1,2", 5), [2, 0, 1])

    def test_garbage_around_valid_tokens(self):
        self.assertEqual(_parse_toggle_indices("1, foo, 2-3, bar", 5), [0, 1, 2])

    def test_lone_dash_dropped(self):
        # leading-dash branch shouldn't be treated as a range
        self.assertEqual(_parse_toggle_indices("-", 5), [])

    def test_trailing_dash_dropped(self):
        self.assertEqual(_parse_toggle_indices("1-", 5), [])


# ── prompt_multi_select ───────────────────────────────────────────────────────

class TestPromptMultiSelect(unittest.TestCase):
    def test_empty_input_applies_initial_state_unchanged(self):
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b", "c"], "Pick", initial_selected=[True, False, True],
            )
        self.assertEqual(result, [True, False, True])

    def test_default_initial_selected_is_all_false(self):
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            result = prompt_multi_select(["a", "b", "c"], "Pick")
        self.assertEqual(result, [False, False, False])

    def test_quit_returns_none(self):
        with patch("builtins.input", return_value="q"), patch("builtins.print"):
            self.assertIsNone(prompt_multi_select(["a", "b"], "Pick"))

    def test_quit_uppercase_returns_none(self):
        with patch("builtins.input", return_value="Q"), patch("builtins.print"):
            self.assertIsNone(prompt_multi_select(["a", "b"], "Pick"))

    def test_quit_word_returns_none(self):
        for word in ("quit", "exit", "QUIT", "Exit"):
            with patch("builtins.input", return_value=word), patch("builtins.print"):
                self.assertIsNone(prompt_multi_select(["a"], "Pick"))

    def test_quit_does_not_apply_pending_toggles(self):
        # toggle then quit — toggles must be discarded
        with patch("builtins.input", side_effect=["1", "q"]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b"], "Pick", initial_selected=[False, False],
            )
        self.assertIsNone(result)

    def test_single_toggle_then_apply(self):
        with patch("builtins.input", side_effect=["2", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b", "c"], "Pick", initial_selected=[False, False, False],
            )
        self.assertEqual(result, [False, True, False])

    def test_toggle_off(self):
        with patch("builtins.input", side_effect=["2", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b", "c"], "Pick", initial_selected=[True, True, True],
            )
        self.assertEqual(result, [True, False, True])

    def test_multiple_toggles_in_single_input(self):
        with patch("builtins.input", side_effect=["1,3", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b", "c"], "Pick", initial_selected=[False, False, False],
            )
        self.assertEqual(result, [True, False, True])

    def test_range_toggle(self):
        with patch("builtins.input", side_effect=["1-3", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b", "c"], "Pick", initial_selected=[False, False, False],
            )
        self.assertEqual(result, [True, True, True])

    def test_multi_step_toggling(self):
        # toggle 1, then toggle 2, then apply
        with patch("builtins.input", side_effect=["1", "2", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b", "c"], "Pick", initial_selected=[False, False, False],
            )
        self.assertEqual(result, [True, True, False])

    def test_toggle_same_index_twice_in_one_input_cancels(self):
        with patch("builtins.input", side_effect=["1,1", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b"], "Pick", initial_selected=[False, False],
            )
        self.assertEqual(result, [False, False])

    def test_toggle_same_index_twice_across_inputs_cancels(self):
        with patch("builtins.input", side_effect=["1", "1", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b"], "Pick", initial_selected=[False, False],
            )
        self.assertEqual(result, [False, False])

    def test_out_of_range_silently_ignored_does_not_apply(self):
        # input is non-empty (so not "apply"), but every token is invalid →
        # nothing toggles, picker keeps prompting
        with patch("builtins.input", side_effect=["99", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b"], "Pick", initial_selected=[True, False],
            )
        self.assertEqual(result, [True, False])

    def test_non_numeric_input_keeps_prompting(self):
        with patch("builtins.input", side_effect=["abc", "1", ""]), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b"], "Pick", initial_selected=[False, False],
            )
        self.assertEqual(result, [True, False])

    def test_whitespace_only_treated_as_empty_apply(self):
        # _prompt strips, so "   " → "" → apply
        with patch("builtins.input", return_value="   "), patch("builtins.print"):
            result = prompt_multi_select(
                ["a"], "Pick", initial_selected=[True],
            )
        self.assertEqual(result, [True])

    def test_empty_items_apply_returns_empty_list(self):
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            result = prompt_multi_select([], "Pick")
        self.assertEqual(result, [])

    def test_empty_items_quit_returns_none(self):
        with patch("builtins.input", return_value="q"), patch("builtins.print"):
            self.assertIsNone(prompt_multi_select([], "Pick"))

    def test_initial_selected_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            prompt_multi_select(["a", "b"], "Pick", initial_selected=[True])

    def test_initial_selected_too_long_raises(self):
        with self.assertRaises(ValueError):
            prompt_multi_select(["a"], "Pick", initial_selected=[True, False])

    def test_initial_selected_truthiness_normalised_to_bool(self):
        # passing 1/0 should still produce a clean list[bool]
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            result = prompt_multi_select(
                ["a", "b"], "Pick", initial_selected=[1, 0],
            )
        self.assertEqual(result, [True, False])
        self.assertTrue(all(isinstance(s, bool) for s in result))

    def test_label_for_called_with_each_item(self):
        seen = []
        def label(item):
            seen.append(item)
            return f'<{item}>'
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            prompt_multi_select(["a", "b", "c"], "Pick", label_for=label)
        self.assertEqual(seen, ["a", "b", "c"])

    def test_label_for_default_uses_str(self):
        # arbitrary objects should render via str() with no callback
        class Obj(object):
            def __str__(self):
                return "rendered"
        with patch("builtins.input", return_value=""), patch("builtins.print") as mock_print:
            prompt_multi_select([Obj()], "Pick")
        printed = ' '.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
        self.assertIn("rendered", printed)

    def test_label_for_receives_original_item_identity(self):
        # label_for must get the *same* object the caller passed, so
        # the consumer can compute custom suffixes from item state
        sentinel = object()
        received = []
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            prompt_multi_select(
                [sentinel], "Pick", label_for=lambda i: received.append(i) or "x",
            )
        self.assertIs(received[0], sentinel)

    def test_items_accepts_any_sequence(self):
        # tuple input shouldn't break — function should list() it internally
        with patch("builtins.input", side_effect=["1", ""]), patch("builtins.print"):
            result = prompt_multi_select(("a", "b"), "Pick")
        self.assertEqual(result, [True, False])

    def test_caller_iterable_not_mutated(self):
        original = ["a", "b", "c"]
        with patch("builtins.input", side_effect=["1,2,3", ""]), patch("builtins.print"):
            prompt_multi_select(original, "Pick", initial_selected=[False] * 3)
        self.assertEqual(original, ["a", "b", "c"])

    def test_initial_selected_iterable_not_mutated(self):
        initial = [False, False, False]
        with patch("builtins.input", side_effect=["1,3", ""]), patch("builtins.print"):
            prompt_multi_select(["a", "b", "c"], "Pick", initial_selected=initial)
        self.assertEqual(initial, [False, False, False])

    def test_render_shows_checkbox_marks(self):
        # both [x] and [ ] should appear when state is mixed
        with patch("builtins.input", return_value=""), patch("builtins.print") as mock_print:
            prompt_multi_select(
                ["a", "b"], "Pick", initial_selected=[True, False],
            )
        printed = '\n'.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
        self.assertIn("[x]", printed)
        self.assertIn("[ ]", printed)

    def test_render_shows_indices_one_based(self):
        with patch("builtins.input", return_value=""), patch("builtins.print") as mock_print:
            prompt_multi_select(["a", "b", "c"], "Pick")
        printed = '\n'.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
        # 1-based numbering — must show "1." not "0."
        self.assertIn("1.", printed)
        self.assertIn("3.", printed)
        self.assertNotIn("0.", printed)

    def test_render_shows_empty_message_when_no_items(self):
        with patch("builtins.input", return_value=""), patch("builtins.print") as mock_print:
            prompt_multi_select(
                [], "Pick", empty_message="<NOTHING HERE>",
            )
        printed = '\n'.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
        self.assertIn("<NOTHING HERE>", printed)

    def test_render_shows_title_each_iteration(self):
        # operator must see the updated table after every toggle round
        # (not just on the first render) — that's the whole point of looping
        title = "PICKER_TITLE_MARKER"
        with patch("builtins.input", side_effect=["1", "2", ""]), patch("builtins.print") as mock_print:
            prompt_multi_select(["a", "b"], title)
        printed_lines = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
        title_renders = sum(1 for line in printed_lines if line == title)
        # 3 input rounds = 3 renders of the title
        self.assertEqual(title_renders, 3)

    def test_full_diff_workflow_matches_consumer_pattern(self):
        # mirrors the REP approval-list use case: caller passes initial
        # state, picker returns final state, caller diffs to compute
        # add/remove operations
        items = ["repo-a", "repo-b", "repo-c", "repo-d"]
        initial = [True, False, True, False]
        # operator: revoke repo-a (toggle 1), approve repo-d (toggle 4)
        with patch("builtins.input", side_effect=["1,4", ""]), patch("builtins.print"):
            final = prompt_multi_select(items, "Pick", initial_selected=initial)
        self.assertEqual(final, [False, False, True, True])
        adds = [i for i, (was, now) in enumerate(zip(initial, final)) if now and not was]
        removes = [i for i, (was, now) in enumerate(zip(initial, final)) if was and not now]
        self.assertEqual(adds, [3])
        self.assertEqual(removes, [0])
