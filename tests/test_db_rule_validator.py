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

    @staticmethod
    def _nested_rule_validator() -> RuleValidator:
        # A `custom_validator` may run another `RuleValidator` over a nested dict or a list of dicts.
        item_rule_validator = RuleValidator(
            [ValueRuleValidator('name', str, nullable=False), ValueRuleValidator('size', int)],
            mandatory_keys=['name'],
        )
        return RuleValidator([
            ValueRuleValidator(
                'items', list, nullable=False,
                custom_validator=lambda items: isinstance(items, list) and all(
                    isinstance(item, dict) and item_rule_validator.validate_dict(item) is not None for item in items),
            ),
            ValueRuleValidator(
                'settings', dict,
                custom_validator=lambda settings: item_rule_validator.validate_dict(settings) is not None,
            ),
        ])

    def test_2_nested_rule_validator_accepts_valid_nested_values(self):
        rules_validator = self._nested_rule_validator()
        payload = {'items': [{'name': 'widget', 'size': 2}, {'name': 'acme'}], 'settings': {'name': 'reviewer'}}
        self.assertDictEqual(rules_validator.validate_dict(payload), payload)
        self.assertDictEqual(rules_validator.validate_dict({'items': []}), {'items': []})

    def test_3_nested_rule_validator_rejects_invalid_nested_values(self):
        rules_validator = self._nested_rule_validator()
        invalid_payloads = [
            {'items': [{'name': 'widget', 'unknown': 1}]},  # key without a rule inside an item
            {'items': [{'size': 2}]},  # mandatory key missing inside an item
            {'items': [{'name': 'widget', 'size': [2]}]},  # wrong type inside an item
            {'items': [42]},  # item is not a dict
            {'items': {}},  # falsy wrong type: core-lib's own type check skips it, the custom_validator does not
            {'items': None},  # not nullable
            {'settings': {'unknown': 1}},  # invalid nested dict
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                self.assertRaises(PermissionError, rules_validator.validate_dict, payload)

    def test_4_nested_rule_validator_keeps_the_inner_reason_as_the_cause(self):
        with self.assertRaises(PermissionError) as context:
            self._nested_rule_validator().validate_dict({'items': [{'size': 2}]})
        self.assertIn('items', str(context.exception))
        self.assertIsInstance(context.exception.__cause__, PermissionError)
        self.assertIn('name', str(context.exception.__cause__))

    def test_6_rule_validators_nest_four_levels_deep(self):
        leaf = RuleValidator([ValueRuleValidator('name', str, nullable=False)], mandatory_keys=['name'])
        level_3 = RuleValidator([ValueRuleValidator(
            'leaf', dict, nullable=False,
            custom_validator=lambda value: leaf.validate_dict(value) is not None,
        )])
        level_2 = RuleValidator([ValueRuleValidator(
            'children', list, nullable=False,
            custom_validator=lambda value: isinstance(value, list) and all(
                isinstance(child, dict) and level_3.validate_dict(child) is not None for child in value),
        )])
        level_1 = RuleValidator([ValueRuleValidator(
            'group', dict, nullable=False,
            custom_validator=lambda value: level_2.validate_dict(value) is not None,
        )])
        root = RuleValidator([ValueRuleValidator(
            'groups', list, nullable=False,
            custom_validator=lambda value: isinstance(value, list) and all(
                isinstance(group, dict) and level_1.validate_dict(group) is not None for group in value),
        )])

        def payload(leaf_value):
            return {'groups': [{'group': {'children': [{'leaf': leaf_value}]}}]}

        valid = payload({'name': 'widget'})
        self.assertDictEqual(root.validate_dict(valid), valid)

        with self.assertRaises(PermissionError) as context:
            root.validate_dict(payload({'name': 'widget', 'unknown': 1}))
        causes = []
        cause = context.exception.__cause__
        while cause is not None:
            causes.append(cause)
            cause = cause.__cause__
        # One chained cause per nested level; the deepest names the rejected key.
        self.assertEqual(len(causes), 4)
        self.assertIn('unknown', str(causes[-1]))

    def test_5_nested_rule_validator_does_not_apply_inner_conversions(self):
        # The inner result is only checked, never returned, so `'2'` is not converted to `2` in the output.
        payload = {'items': [{'name': 'widget', 'size': '2'}]}
        self.assertDictEqual(self._nested_rule_validator().validate_dict(payload), payload)
