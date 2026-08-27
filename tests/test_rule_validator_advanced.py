import unittest
import datetime

from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.rule_validator.rule_validator_decorator import ParameterRuleValidator


class TestRuleValidatorTypeCoercions(unittest.TestCase):
    def test_int_to_str_coercion(self):
        rules = RuleValidator([ValueRuleValidator('name', str)])
        result = rules.validate_dict({'name': 42})
        self.assertEqual(result['name'], '42')

    def test_float_to_str_coercion(self):
        rules = RuleValidator([ValueRuleValidator('score', str)])
        result = rules.validate_dict({'score': 3.14})
        self.assertEqual(result['score'], '3.14')

    def test_digit_str_to_int_coercion(self):
        rules = RuleValidator([ValueRuleValidator('age', int)])
        result = rules.validate_dict({'age': '25'})
        self.assertEqual(result['age'], 25)

    def test_non_digit_str_to_int_raises(self):
        rules = RuleValidator([ValueRuleValidator('age', int)])
        self.assertRaises(PermissionError, rules.validate_dict, {'age': 'abc'})

    def test_str_to_datetime_coercion(self):
        rules = RuleValidator([ValueRuleValidator('created_at', datetime.datetime)])
        result = rules.validate_dict({'created_at': '2023-06-15T10:30:00'})
        self.assertIsInstance(result['created_at'], datetime.datetime)
        self.assertEqual(result['created_at'].year, 2023)

    def test_str_to_date_coercion(self):
        rules = RuleValidator([ValueRuleValidator('dob', datetime.date)])
        result = rules.validate_dict({'dob': '1990-01-01'})
        self.assertIsInstance(result['dob'], datetime.datetime)

    def test_invalid_datetime_str_raises(self):
        rules = RuleValidator([ValueRuleValidator('ts', datetime.datetime)])
        self.assertRaises(PermissionError, rules.validate_dict, {'ts': 'not-a-date'})

    def test_wrong_type_raises(self):
        rules = RuleValidator([ValueRuleValidator('count', int)])
        self.assertRaises(PermissionError, rules.validate_dict, {'count': [1, 2, 3]})


class TestRuleValidatorNullable(unittest.TestCase):
    def test_nullable_true_accepts_none(self):
        rules = RuleValidator([ValueRuleValidator('name', str, nullable=True)])
        result = rules.validate_dict({'name': None})
        self.assertIsNone(result['name'])

    def test_nullable_false_rejects_none(self):
        rules = RuleValidator([ValueRuleValidator('name', str, nullable=False)])
        self.assertRaises(PermissionError, rules.validate_dict, {'name': None})


class TestRuleValidatorCustomConverter(unittest.TestCase):
    def test_custom_converter_applied(self):
        rules = RuleValidator([ValueRuleValidator('name', str, custom_converter=str.upper)])
        result = rules.validate_dict({'name': 'hello'})
        self.assertEqual(result['name'], 'HELLO')

    def test_custom_converter_takes_priority_over_type_coercion(self):
        converter = lambda v: int(v) * 2
        rules = RuleValidator([ValueRuleValidator('val', int, custom_converter=converter)])
        result = rules.validate_dict({'val': '5'})
        self.assertEqual(result['val'], 10)


class TestRuleValidatorUpdateRemove(unittest.TestCase):
    def test_update_adds_new_rule(self):
        rules = RuleValidator([ValueRuleValidator('name', str)])
        rules.update([ValueRuleValidator('age', int)])
        result = rules.validate_dict({'name': 'Alice', 'age': 30})
        self.assertEqual(result['age'], 30)

    def test_update_rejects_non_rule_validator(self):
        rules = RuleValidator([])
        self.assertRaises(ValueError, rules.update, ['not_a_validator'])

    def test_remove_existing_rule(self):
        rules = RuleValidator([ValueRuleValidator('name', str), ValueRuleValidator('age', int)])
        rules.remove('age')
        self.assertNotIn('age', rules.rules)

    def test_remove_nonexistent_key_no_error(self):
        rules = RuleValidator([ValueRuleValidator('name', str)])
        rules.remove('nonexistent')


class TestParameterRuleValidator(unittest.TestCase):
    def setUp(self):
        self.rules = RuleValidator([ValueRuleValidator('name', str), ValueRuleValidator('age', int)])

    def test_validates_target_parameter(self):
        @ParameterRuleValidator(self.rules, 'data')
        def update(self_ref, data: dict):
            return data

        result = update(None, {'name': 'Alice', 'age': 30})
        self.assertEqual(result['name'], 'Alice')
        self.assertEqual(result['age'], 30)

    def test_rejects_invalid_value(self):
        @ParameterRuleValidator(self.rules, 'data')
        def update(self_ref, data: dict):
            return data

        self.assertRaises(PermissionError, update, None, {'name': 'Alice', 'unknown_key': 'x'})

    def test_non_dict_parameter_raises(self):
        @ParameterRuleValidator(self.rules, 'data')
        def update(self_ref, data):
            return data

        self.assertRaises(ValueError, update, None, 'not_a_dict')

    def test_missing_parameter_name_raises(self):
        self.assertRaises(ValueError, ParameterRuleValidator, self.rules, '')

    def test_missing_rule_validator_raises(self):
        self.assertRaises(ValueError, ParameterRuleValidator, None, 'data')

    def test_additional_validators_applied_then_removed(self):
        extra = ValueRuleValidator('extra_field', str)

        @ParameterRuleValidator(self.rules, 'data')
        def update(self_ref, data: dict, **kwargs):
            return data

        result = update(None, {'name': 'Bob', 'extra_field': 'yes'}, additional_validators=[extra])
        self.assertEqual(result['extra_field'], 'yes')
        self.assertNotIn('extra_field', self.rules.rules)
