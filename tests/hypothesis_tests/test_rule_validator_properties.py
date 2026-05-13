"""Property-based tests for rule_validator.rule_validator.RuleValidator."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.rule_validator.rule_validator import (
    RuleValidator,
    ValueRuleValidator,
)
from tests.hypothesis_tests._settings import SETTINGS


_VALID_NAMES = st.text(alphabet=stringmod.ascii_lowercase, min_size=1, max_size=10)


class TestRuleValidatorProperties(unittest.TestCase):
    @given(value=st.text(min_size=0, max_size=50))
    @SETTINGS
    def test_str_rule_passes_strings_through(self, value):
        rv = RuleValidator([ValueRuleValidator('k', str)])
        out = rv.validate_dict({'k': value}, strict_mode=False)
        self.assertEqual(out['k'], value)

    @given(value=st.integers(min_value=-10000, max_value=10000))
    @SETTINGS
    def test_int_rule_passes_integers_through(self, value):
        rv = RuleValidator([ValueRuleValidator('k', int)])
        out = rv.validate_dict({'k': value}, strict_mode=False)
        self.assertEqual(out['k'], value)

    @given(value=st.integers(min_value=0, max_value=10000))
    @SETTINGS
    def test_digit_str_coerced_to_int(self, value):
        rv = RuleValidator([ValueRuleValidator('k', int)])
        out = rv.validate_dict({'k': str(value)}, strict_mode=False)
        self.assertEqual(out['k'], value)

    @given(value=st.integers().filter(lambda n: n != 0))
    @SETTINGS
    def test_int_rule_str_target_coerces_nonzero_int_to_str(self, value):
        # NOTE: production code uses `if value and ...` so falsy values (0)
        # short-circuit and skip coercion — covered by the explicit test below.
        rv = RuleValidator([ValueRuleValidator('k', str)])
        out = rv.validate_dict({'k': value}, strict_mode=False)
        self.assertEqual(out['k'], str(value))

    def test_int_rule_str_target_zero_passes_through(self):
        # Document the behavior surfaced by hypothesis: 0 is falsy, so the
        # `if value and ...` coercion guard skips. The validator simply
        # returns the value unchanged.
        rv = RuleValidator([ValueRuleValidator('k', str)])
        out = rv.validate_dict({'k': 0}, strict_mode=False)
        self.assertEqual(out['k'], 0)

    @given(
        names=st.lists(_VALID_NAMES, min_size=1, max_size=10, unique=True),
    )
    @SETTINGS
    def test_update_and_remove_round_trip(self, names):
        rv = RuleValidator([])
        rv.update([ValueRuleValidator(n, str) for n in names])
        # All registered
        for n in names:
            self.assertIn(n, rv.rules)
        # Remove all
        for n in names:
            rv.remove(n)
        # None remaining
        for n in names:
            self.assertNotIn(n, rv.rules)

    @given(
        names=st.lists(_VALID_NAMES, min_size=1, max_size=5, unique=True),
        value=st.text(min_size=1, max_size=10),
    )
    @SETTINGS
    def test_prohibited_key_always_raises(self, names, value):
        rv = RuleValidator(
            [ValueRuleValidator(n, str) for n in names],
            prohibited_keys=names,
        )
        # Any one of the prohibited keys triggers PermissionError
        target = names[0]
        with self.assertRaises(PermissionError):
            rv.validate_dict({target: value}, strict_mode=False)

    @given(
        present_keys=st.lists(_VALID_NAMES, min_size=1, max_size=5, unique=True),
    )
    @SETTINGS
    def test_mandatory_missing_raises(self, present_keys):
        # Add one rule for each present key, then make a different name mandatory
        rules = [ValueRuleValidator(n, str) for n in present_keys]
        rv = RuleValidator(rules, mandatory_keys=['_definitely_missing_'])
        with self.assertRaises(PermissionError):
            rv.validate_dict(
                {n: 'v' for n in present_keys}, strict_mode=False
            )
