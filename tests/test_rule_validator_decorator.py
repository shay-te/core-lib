"""@ParameterRuleValidator validates and converts one dict argument before the decorated method runs."""
import unittest

from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator
from core_lib.rule_validator.rule_validator_decorator import ParameterRuleValidator


def widget_rules(strict_mode: bool = True, strict_output: bool = False) -> RuleValidator:
    # A fresh RuleValidator per test: `additional_validators` changes the one it is given.
    return RuleValidator(
        [ValueRuleValidator('name', str), ValueRuleValidator('height', int)],
        strict_mode=strict_mode,
        strict_output=strict_output,
    )


def make_update(rule_validator: RuleValidator, **decorator_kwargs):
    @ParameterRuleValidator(rule_validator, 'data', **decorator_kwargs)
    def update(widget_id: int, data: dict, additional_validators: list = None):
        return widget_id, data

    return update


class WidgetStore(object):
    def __init__(self):
        self.updates = []

    @ParameterRuleValidator(widget_rules(), 'data')
    def update(self, widget_id: int, data: dict):
        self.updates.append((widget_id, data))
        return len(self.updates)


class TestRuleValidatorDecorator(unittest.TestCase):

    def test_method_receives_the_converted_dict(self):
        store = WidgetStore()

        self.assertEqual(1, store.update(7, {'name': 'acme', 'height': '180'}))

        self.assertEqual([(7, {'name': 'acme', 'height': 180})], store.updates)

    def test_invalid_dict_never_reaches_the_method(self):
        store = WidgetStore()

        with self.assertRaises(PermissionError):
            store.update(7, {'height': 'tall'})
        with self.assertRaises(PermissionError):
            store.update(7, {'colour': 'red'})   # no rule, and the RuleValidator is strict

        self.assertEqual([], store.updates)

    def test_strict_mode_none_uses_the_rule_validators_own(self):
        lenient_update = make_update(widget_rules(strict_mode=False, strict_output=True))
        # strict_output is not passed on by the decorator, so the unknown key is kept, not dropped
        self.assertEqual((7, {'name': 'acme', 'colour': 'red'}), lenient_update(7, {'name': 'acme', 'colour': 'red'}))

        strict_update = make_update(widget_rules(strict_mode=False), strict_mode=True)
        with self.assertRaises(PermissionError):
            strict_update(7, {'name': 'acme', 'colour': 'red'})

    def test_mandatory_and_prohibited_keys(self):
        update = make_update(widget_rules(), mandatory_keys=['name'], prohibited_keys=['height'])

        self.assertEqual((7, {'name': 'acme'}), update(7, {'name': 'acme'}))
        with self.assertRaises(PermissionError):
            update(7, {})
        with self.assertRaises(PermissionError):
            update(7, {'name': 'acme', 'height': 180})

    def test_additional_validators_apply_to_one_call_only(self):
        update = make_update(widget_rules())
        colour_rule = ValueRuleValidator('colour', str)

        self.assertEqual(
            (7, {'name': 'acme', 'colour': 'red'}),
            update(7, {'name': 'acme', 'colour': 'red'}, additional_validators=[colour_rule]),
        )

        with self.assertRaises(PermissionError):
            update(7, {'colour': 'red'})
        self.assertEqual((7, {'name': 'acme'}), update(7, {'name': 'acme'}))

    def test_dict_passed_as_keyword_is_not_validated(self):
        # Documented: the decorator finds the dict by position only.
        update = make_update(widget_rules())

        with self.assertRaises(IndexError):
            update(7, data={'height': 'tall'})

    def test_argument_that_is_not_a_dict_raises(self):
        update = make_update(widget_rules())

        with self.assertRaises(ValueError) as context:
            update(7, [('name', 'acme')])

        self.assertIn('function `update`, parameter `data`', str(context.exception))

    def test_constructor_requires_a_parameter_name_and_a_rule_validator(self):
        with self.assertRaises(ValueError) as no_parameter:
            ParameterRuleValidator(widget_rules(), '')
        self.assertEqual('ParameterRuleValidator: parameter_name missing', str(no_parameter.exception))

        with self.assertRaises(ValueError) as no_rule_validator:
            ParameterRuleValidator(None, 'data')
        self.assertEqual('ParameterRuleValidator: rule_validator missing', str(no_rule_validator.exception))
