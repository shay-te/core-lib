"""Challenge tests for RuleValidator flag combinations.

The 4 boolean/list flags give 16 combinations on the constructor and 16 on each
validate_dict() call. We don't test all 256 — but we cover the meaningful axes:
- strict_mode True/False vs ctor default
- strict_output True/False vs ctor default
- mandatory_keys at ctor vs validate_dict override
- prohibited_keys at ctor vs validate_dict override
- nullable True/False per rule
- custom_converter / custom_validator paired and separate
"""
import datetime
import unittest

from core_lib.rule_validator.rule_validator import (
    RuleValidator,
    ValueRuleValidator,
)


def _rules():
    return [
        ValueRuleValidator('name', str),
        ValueRuleValidator('age', int),
        ValueRuleValidator('opt', str, nullable=True),
        ValueRuleValidator('required_field', str, nullable=False),
    ]


class TestRuleValidatorStrictMode(unittest.TestCase):
    def test_strict_mode_true_unknown_key_raises(self):
        rv = RuleValidator(_rules(), strict_mode=True)
        with self.assertRaises(PermissionError):
            rv.validate_dict({'unknown': 'x'})

    def test_strict_mode_false_unknown_key_included(self):
        rv = RuleValidator(_rules(), strict_mode=False)
        # validate_dict uses strict_mode arg default `True` if caller doesn't
        # pass anything → uses self.strict_mode is False so the False branch.
        out = rv.validate_dict({'unknown': 'x'}, strict_mode=False)
        self.assertEqual(out['unknown'], 'x')

    def test_strict_mode_false_strict_output_true_drops_unknown(self):
        rv = RuleValidator(_rules(), strict_mode=False, strict_output=True)
        out = rv.validate_dict({'unknown': 'x'}, strict_mode=False, strict_output=True)
        self.assertNotIn('unknown', out)


class TestRuleValidatorMandatoryKeys(unittest.TestCase):
    def test_ctor_mandatory_keys_required(self):
        rv = RuleValidator(_rules(), mandatory_keys=['name'])
        with self.assertRaises(PermissionError):
            rv.validate_dict({'age': 30}, strict_mode=False)

    def test_per_call_mandatory_overrides_ctor(self):
        rv = RuleValidator(_rules(), mandatory_keys=['name'])
        # Per-call mandatory overrides ctor — provide age instead
        out = rv.validate_dict({'age': 30}, strict_mode=False, mandatory_keys=['age'])
        self.assertEqual(out['age'], 30)

    def test_per_call_empty_falls_back_to_ctor(self):
        # `mandatory_keys or self.mandatory_keys` — empty list is falsy, so
        # passing [] falls back to ctor's ['name'] which is still enforced.
        rv = RuleValidator(_rules(), mandatory_keys=['name'])
        with self.assertRaises(PermissionError):
            rv.validate_dict({'age': 30}, strict_mode=False, mandatory_keys=[])


class TestRuleValidatorProhibitedKeys(unittest.TestCase):
    def test_ctor_prohibited_raises(self):
        rv = RuleValidator(_rules(), prohibited_keys=['name'])
        with self.assertRaises(PermissionError):
            rv.validate_dict({'name': 'a'}, strict_mode=False)

    def test_per_call_prohibited_overrides(self):
        rv = RuleValidator(_rules(), prohibited_keys=['name'])
        # Override: prohibit something different
        rv.validate_dict({'name': 'a'}, strict_mode=False, prohibited_keys=['age'])


class TestRuleValidatorNullable(unittest.TestCase):
    def test_nullable_true_accepts_none(self):
        rv = RuleValidator(_rules())
        out = rv.validate_dict({'opt': None}, strict_mode=False)
        self.assertIsNone(out['opt'])

    def test_nullable_false_rejects_none(self):
        rv = RuleValidator(_rules())
        with self.assertRaises(PermissionError):
            rv.validate_dict({'required_field': None}, strict_mode=False)

    def test_nullable_with_custom_validator_returning_false(self):
        # When nullable=True and value is None, custom_validator can return
        # something not-True without erroring (the `is_allow_null` short-circuit).
        rule = ValueRuleValidator(
            'k', int, nullable=True, custom_validator=lambda v: v == 42
        )
        rv = RuleValidator([rule])
        # None is allowed → no error even though validator returns False
        out = rv.validate_dict({'k': None})
        self.assertIsNone(out['k'])


class TestRuleValidatorCustomConverter(unittest.TestCase):
    def test_converter_runs_before_validator(self):
        rule = ValueRuleValidator(
            'k', int,
            custom_converter=lambda v: int(v) * 10,
            custom_validator=lambda v: v % 10 == 0,
        )
        rv = RuleValidator([rule])
        out = rv.validate_dict({'k': '5'}, strict_mode=False)
        self.assertEqual(out['k'], 50)

    def test_converter_only(self):
        rule = ValueRuleValidator('k', int, custom_converter=lambda v: 99)
        rv = RuleValidator([rule])
        out = rv.validate_dict({'k': 'anything'}, strict_mode=False)
        self.assertEqual(out['k'], 99)

    def test_validator_only(self):
        rule = ValueRuleValidator('k', int, custom_validator=lambda v: v > 0)
        rv = RuleValidator([rule])
        out = rv.validate_dict({'k': 10}, strict_mode=False)
        self.assertEqual(out['k'], 10)

    def test_validator_failure_raises(self):
        rule = ValueRuleValidator('k', int, custom_validator=lambda v: v > 100)
        rv = RuleValidator([rule])
        with self.assertRaises(PermissionError):
            rv.validate_dict({'k': 5}, strict_mode=False)

    def test_validator_raising_wraps(self):
        rule = ValueRuleValidator(
            'k', int, custom_validator=lambda v: (_ for _ in ()).throw(KeyError('inside'))
        )
        rv = RuleValidator([rule])
        with self.assertRaises(PermissionError):
            rv.validate_dict({'k': 5}, strict_mode=False)


class TestRuleValidatorTypeCoercion(unittest.TestCase):
    """Spot-check every documented type coercion path."""

    def setUp(self):
        self.rv = RuleValidator(
            [
                ValueRuleValidator('s', str),
                ValueRuleValidator('i', int),
                ValueRuleValidator('dt', datetime.datetime),
                ValueRuleValidator('d', datetime.date),
                ValueRuleValidator('lst', list),
            ]
        )

    def test_int_to_str(self):
        self.assertEqual(
            self.rv.validate_dict({'s': 42}, strict_mode=False)['s'], '42'
        )

    def test_float_to_str(self):
        self.assertEqual(
            self.rv.validate_dict({'s': 3.14}, strict_mode=False)['s'], '3.14'
        )

    def test_digit_str_to_int(self):
        self.assertEqual(
            self.rv.validate_dict({'i': '42'}, strict_mode=False)['i'], 42
        )

    def test_negative_str_to_int_raises(self):
        # '-5'.isdigit() is False, so this raises
        with self.assertRaises(PermissionError):
            self.rv.validate_dict({'i': '-5'}, strict_mode=False)

    def test_str_to_datetime_iso(self):
        out = self.rv.validate_dict({'dt': '2024-01-15T12:30:00'}, strict_mode=False)
        self.assertIsInstance(out['dt'], datetime.datetime)

    def test_str_to_datetime_invalid_raises(self):
        with self.assertRaises(PermissionError):
            self.rv.validate_dict({'dt': 'garbage'}, strict_mode=False)

    def test_str_to_date_iso(self):
        out = self.rv.validate_dict({'d': '2024-01-15'}, strict_mode=False)
        # dateutil returns datetime; the value_type check passes for date via
        # subclass.
        self.assertIsNotNone(out['d'])

    def test_wrong_type_for_list_raises(self):
        with self.assertRaises(PermissionError):
            self.rv.validate_dict({'lst': 'not a list'}, strict_mode=False)


class TestRuleValidatorUpdateRemove(unittest.TestCase):
    def test_update_adds_new_rules(self):
        rv = RuleValidator([])
        rv.update([ValueRuleValidator('k', str)])
        out = rv.validate_dict({'k': 'v'}, strict_mode=False)
        self.assertEqual(out['k'], 'v')

    def test_update_replaces_existing(self):
        rv = RuleValidator([ValueRuleValidator('k', str)])
        rv.update([ValueRuleValidator('k', int)])
        out = rv.validate_dict({'k': 42}, strict_mode=False)
        self.assertEqual(out['k'], 42)

    def test_update_rejects_non_value_rule_validator(self):
        rv = RuleValidator([])
        with self.assertRaises(ValueError):
            rv.update([{'key': 'k', 'value_type': str}])

    def test_remove_existing(self):
        rv = RuleValidator([ValueRuleValidator('k', str)])
        rv.remove('k')
        self.assertNotIn('k', rv.rules)

    def test_remove_missing_no_op(self):
        rv = RuleValidator([])
        rv.remove('nothing-here')

    def test_empty_dict_returns_empty(self):
        rv = RuleValidator([ValueRuleValidator('k', str)])
        self.assertEqual(rv.validate_dict({}), {})
