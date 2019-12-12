import unittest
import enum
from core_lib.decorators.validator import RuleValidator, _validate_dict_by_rules

USER_SEARCH_PREFERENCES_MIN_AGE = 18
USER_SEARCH_PREFERENCES_MAX_AGE = 90


class TestUpdateValidate(unittest.TestCase):

    def test_1_expressions(self):
        class Gender(enum.Enum):
            FEMALE = enum.auto()
            MALE = enum.auto()

        allowed_update_types = {
            'gender': RuleValidator(int, True, lambda value: 0 <= value <= len(Gender)),
            'orientation': RuleValidator(int, True),
            'age_from': RuleValidator(int, False, lambda value: 0 <= value > USER_SEARCH_PREFERENCES_MIN_AGE),
            'age_to': RuleValidator(int, False, lambda value: 0 <= value < USER_SEARCH_PREFERENCES_MAX_AGE),
            'location_mode': RuleValidator(int, True),
            'city_id': RuleValidator(int, True),
            'radius': RuleValidator(int, True)
        }

        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'gender': -1})
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'gender': 3})
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'gender': ''})
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'shastalkata': 11 })
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'age_from': (USER_SEARCH_PREFERENCES_MIN_AGE-1)})
        self.assertRaises(PermissionError, _validate_dict_by_rules, allowed_update_types, {'age_to': (USER_SEARCH_PREFERENCES_MAX_AGE+1)})


