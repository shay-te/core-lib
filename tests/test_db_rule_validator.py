import datetime
import enum
import unittest

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
            ValueRuleValidator(
                'age_from', int, nullable=False, custom_validator=lambda value: 0 <= value > USER_MIN_AGE
            ),
            ValueRuleValidator('age_to', int, nullable=False, custom_validator=lambda value: 0 <= value < USER_MAX_AGE),
            ValueRuleValidator('location_mode', int),
            ValueRuleValidator('radius', int),
            ValueRuleValidator('email', str),
            ValueRuleValidator('prohibited_key', str),
        ]

        rules_validator = RuleValidator(allowed_update_types, mandatory_keys=['gender'], prohibited_keys=['email'])

        # No rule for key `shastalkata`
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'shastalkata': 11})
        # Invalid gender. custom_validator fail
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': -1})
        # Invalid gender. custom_validator fail
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 3})
        # Invalid gender. not a number
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': ''})
        # less than min age
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'age_from': (USER_MIN_AGE - 1)})
        # greater than max age
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'age_to': (USER_MAX_AGE + 1)})
        # mandatory_keys gender missing
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'radius': 1})
        # prohibited_keys email
        self.assertRaises(PermissionError, rules_validator.validate_dict, {'gender': 1, 'email': 'email@gmail.com'})
        self.assertRaises(
            PermissionError,
            rules_validator.validate_dict,
            {'gender': 1, 'prohibited_key': 'value'},
            prohibited_keys='prohibited_key',
        )  # prohibited_keys locally on the function

        try:
            rules_validator.validate_dict({'gender': 1, 'new_field_i_am': 'value'}, strict_mode=False)
        except PermissionError:
            self.fail("`strict_mode=False`. new field introduced without a rule defined.")

        json_data = {
            'gender': 1,
            'email': 'email@gmail.com',
            'age_from': (USER_MIN_AGE + 2),
            'age_to': (USER_MAX_AGE - 2),
            'new_field_i_am': 'value',
            'prohibited_key': 'value',
        }
        self.assertDictEqual(
            rules_validator.validate_dict(
                json_data, strict_mode=False, prohibited_keys=["now_key_to_reset_the_forhibeded_email"]
            ),
            json_data,
        )

        new_dict = rules_validator.validate_dict(
            json_data, strict_mode=False, strict_output=True, prohibited_keys=["now_key_to_reset_the_forhibeded_email"]
        )
        self.assertNotIn('new_field_i_am', new_dict)
        self.assertEqual(len(new_dict), 5)

    def test_converts_what_it_safely_can(self):
        rules_validator = RuleValidator([
            ValueRuleValidator('name', str),
            ValueRuleValidator('height', int),
            ValueRuleValidator('born', datetime.date),
            ValueRuleValidator('seen_at', datetime.datetime),
        ])

        validated = rules_validator.validate_dict(
            {'name': 42, 'height': '180', 'born': '1990-04-01', 'seen_at': '2024-06-14T09:30:00'}
        )

        self.assertEqual(
            {
                'name': '42',
                'height': 180,
                'born': datetime.datetime(1990, 4, 1),   # a `date` rule still gives a datetime
                'seen_at': datetime.datetime(2024, 6, 14, 9, 30),
            },
            validated,
        )
        self.assertIs(int, type(validated['height']))
        self.assertEqual({'name': '1.5'}, rules_validator.validate_dict({'name': 1.5}))

    def test_rejects_what_it_cannot_convert(self):
        rules_validator = RuleValidator([
            ValueRuleValidator('height', int),
            ValueRuleValidator('born', datetime.date),
            ValueRuleValidator('tags', list),
        ])
        for update in (
            {'height': 'tall'},
            {'height': '-5'},          # only a plain string of digits converts
            {'height': '1.5'},
            {'height': 1.5},
            {'born': 'not a date'},
            {'born': '1990-13-45'},
            {'tags': 'acme'},
        ):
            with self.assertRaises(PermissionError, msg=update):
                rules_validator.validate_dict(update)

        with self.assertRaises(PermissionError) as bad_date:
            rules_validator.validate_dict({'born': '1990-13-45'})
        self.assertIsNotNone(bad_date.exception.__cause__)   # the parser's own error is kept

        with self.assertRaises(PermissionError) as bad_type:
            rules_validator.validate_dict({'tags': 'acme'})
        self.assertEqual("Invalid update key:`tags` illegal type `<class 'str'>` expected <class 'list'>", str(bad_type.exception))

    def test_falsy_values_skip_the_type_check(self):
        rules_validator = RuleValidator([ValueRuleValidator('height', int), ValueRuleValidator('name', str)])
        self.assertEqual({'height': '', 'name': 0}, rules_validator.validate_dict({'height': '', 'name': 0}))

    def test_not_nullable_rejects_none(self):
        rules_validator = RuleValidator([
            ValueRuleValidator('name', str, nullable=False),
            ValueRuleValidator('nick_name', str),
        ])
        with self.assertRaises(PermissionError):
            rules_validator.validate_dict({'name': None})
        self.assertEqual({'nick_name': None}, rules_validator.validate_dict({'nick_name': None}))

    def test_update_adds_or_replaces_rules_and_remove_drops_one(self):
        rules_validator = RuleValidator([ValueRuleValidator('height', int)])

        rules_validator.update([ValueRuleValidator('height', str), ValueRuleValidator('name', str)])
        self.assertEqual({'height': '180', 'name': 'acme'}, rules_validator.validate_dict({'height': 180, 'name': 'acme'}))

        rules_validator.remove('name')
        rules_validator.remove('never_added')   # an absent key is ignored
        with self.assertRaises(PermissionError):
            rules_validator.validate_dict({'name': 'acme'})
        self.assertEqual({'height': '7'}, rules_validator.validate_dict({'height': 7}))

    def test_rules_must_be_value_rule_validators(self):
        with self.assertRaises(ValueError):
            RuleValidator(['height'])

        rules_validator = RuleValidator([ValueRuleValidator('height', int)])
        with self.assertRaises(ValueError):
            rules_validator.update([{'key': 'name', 'value_type': str}])
        self.assertEqual({'height': 7}, rules_validator.validate_dict({'height': 7}))
