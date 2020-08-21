import unittest
import enum

from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator

USER_MIN_AGE = 18
USER_MAX_AGE = 90


class TestUpdateValidate(unittest.TestCase):

    def test_1_expressions(self):
        class Gender(enum.Enum):
            FEMALE = enum.auto()
            MALE = enum.auto()

        allowed_update_types = [
            ValueRuleValidator('gender', int, custom_validator=lambda value: 0 <= value <= len(Gender)),
            ValueRuleValidator('orientation', int),
            ValueRuleValidator('age_from', int, nullable=False, custom_validator=lambda value: 0 <= value > USER_MIN_AGE),
            ValueRuleValidator('age_to', int, nullable=False, custom_validator=lambda value: 0 <= value < USER_MAX_AGE),
            ValueRuleValidator('location_mode', int),
            ValueRuleValidator('radius', int),
            ValueRuleValidator('email', str),
            ValueRuleValidator('prohibited_key', str),
        ]

        rules_validator = RuleValidator(allowed_update_types, mandatory_keys=['gender'], prohibited_keys=['email'])

        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'shastalkata': 11})  # No rule for key `shastalkata`
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': -1})  # Invalid gender. custom_validator fail
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 3})  # Invalid gender. custom_validator fail
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': ''})  # Invalid gender. not a number
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'age_from': (USER_MIN_AGE - 1)})  # less then min age
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'age_to': (USER_MAX_AGE + 1)}) # greater then max age
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'radius': 1})  # mandatory_keys gender missing
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'email': 'email@gmail.com'})  # prohibited_keys email
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'prohibited_key': 'value'}, prohibited_keys='prohibited_key')  # prohibited_keys locally on the function

        try:
            rules_validator.validate_dict({'gender': 1, 'new_field_i_am': 'value'}, strict_mode=False)
        except PermissionError:
            self.fail("`strict_mode=False`. new field introduced without a rule defined.")

        json_data = {'gender': 1,
                     'email': 'email@gmail.com',
                     'age_from': (USER_MIN_AGE + 2),
                     'age_to': (USER_MAX_AGE - 2),
                     'new_field_i_am': 'value',
                     'prohibited_key': 'value'}
        self.assertDictEqual(rules_validator.validate_dict(json_data, strict_mode=False, prohibited_keys=["now_key_to_reset_the_forhibeded_email"]), json_data)

        new_dict = rules_validator.validate_dict(json_data, strict_mode=False, strict_output=True, prohibited_keys=["now_key_to_reset_the_forhibeded_email"])
        self.assertNotIn('new_field_i_am', new_dict)
        self.assertEqual(len(new_dict), 5)
