import unittest
import enum

from core_lib.rule_validator.validator import RuleValidator, _validate_dict_by_rules

USER_MIN_AGE = 18
USER_MAX_AGE = 90


class TestUpdateValidate(unittest.TestCase):

    def test_1_expressions(self):
        class Gender(enum.Enum):
            FEMALE = enum.auto()
            MALE = enum.auto()

        allowed_update_types = {
            'gender': RuleValidator(int, lambda value: 0 <= value <= len(Gender)),
            'orientation': RuleValidator(int),
            'age_from': RuleValidator(int, nullable=False, custom_validator=lambda value: 0 <= value > USER_MIN_AGE),
            'age_to': RuleValidator(int, nullable=False, custom_validator=lambda value: 0 <= value < USER_MAX_AGE),
            'location_mode': RuleValidator(int),
            'city_id': RuleValidator(int),
            'radius': RuleValidator(int)
        }

        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'gender': -1})
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'gender': 3})
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'gender': ''})
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'shastalkata': 11 })
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'age_from': (USER_MIN_AGE - 1)})
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'age_to': (USER_MAX_AGE + 1)})


