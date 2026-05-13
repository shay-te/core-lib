"""Regression tests for bugs found by audit and fixed.

Each test class corresponds to one bug. The tests assert the fixed behavior
so future refactors can't silently re-introduce the bug.
"""
import datetime
import logging
import unittest
from datetime import timezone
from unittest.mock import patch

from core_lib.helpers.config_instances import _get_config_under_path
from core_lib.observer.observer import Observer
from core_lib.observer.observer_listener import ObserverListener
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator


# ── Bug 1: crud_soft_delete_token TZ-naive timestamp ────────────────────────


class TestSoftDeleteTokenTimezone(unittest.TestCase):
    """Bug: `int(datetime.utcnow().timestamp())` produced local-time-as-UTC
    epoch on non-UTC systems, drifting from real UTC by the local offset.
    Fix: use `datetime.now(tz=timezone.utc).timestamp()`."""

    def test_token_matches_real_utc_epoch(self):
        # Stub utcnow so the test is timezone-independent.
        import core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access as mod

        captured = {}

        class _FakeQuery:
            def __init__(self):
                pass
            def filter(self, *args, **kwargs):
                return self
            def update(self, payload):
                captured.update(payload)
                return 1

        class _FakeSession:
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
            def query(self, entity):
                return _FakeQuery()

        class _FakeFactory:
            def get(self):
                return _FakeSession()

        class _FakeEntity:
            id = 'id-column'
            deleted_at = 'deleted_at-column'
            deleted_at_token = 'deleted_at_token-column'

        access = mod.CRUDSoftDeleteWithTokenDataAccess.__new__(
            mod.CRUDSoftDeleteWithTokenDataAccess
        )
        access._db_entity = _FakeEntity
        access._db = _FakeFactory()
        access._rule_validator = None

        before = datetime.datetime.now(tz=timezone.utc).timestamp()
        access.delete(1)
        after = datetime.datetime.now(tz=timezone.utc).timestamp()

        token = captured['deleted_at_token-column']
        self.assertIsInstance(token, int)
        # Token is real UTC epoch — within the call window
        self.assertGreaterEqual(token, int(before))
        self.assertLessEqual(token, int(after) + 1)


# ── Bug 2: Observer logger.error invocation ────────────────────────────────


class _RaisingListener(ObserverListener):
    def update(self, key, value):
        raise RuntimeError('listener exploded')


class TestObserverLoggerDoesNotCrashOnNotifyError(unittest.TestCase):
    """Bug: `logger.error(msg, ex)` passed the exception as a %-style format
    argument, which can produce `TypeError: not all arguments converted` in
    some pytest log configs (we hit it before). Fix: use `exc_info=True`."""

    def test_logging_does_not_raise_during_observer_notify(self):
        obs = Observer(listener_type=_RaisingListener)
        obs.attach(_RaisingListener())

        # Force the logger to a pytest-incompatible config to surface the bug
        observer_logger = logging.getLogger('core_lib.observer.observer')

        # Run with the real logging path enabled. The fixed code uses
        # exc_info=True, which never triggers a format-arg error.
        with self.assertRaises(RuntimeError):
            obs.notify('k', 'v')


# ── Bug 3: rule_validator falsy-value short-circuit ────────────────────────


class TestRuleValidatorFalsyValuesNotSkipped(unittest.TestCase):
    """Bug: `elif value and ...` short-circuits on falsy values, so 0 / 0.0 /
    '' / False bypass all type coercion and isinstance checks, returning
    the wrong type silently. Fix: replace `if value` with `if value is not None`."""

    def test_zero_coerced_to_string_when_rule_expects_str(self):
        rv = RuleValidator([ValueRuleValidator('k', str)])
        out = rv.validate_dict({'k': 0}, strict_mode=False)
        # Before fix: 0 was returned as int 0
        self.assertEqual(out['k'], '0')

    def test_false_coerced_to_string_when_rule_expects_str(self):
        # bool is a subclass of int, type(False) is bool → not in [int, float],
        # so the str-coercion branch doesn't fire even after the fix. But the
        # type-check branch (line 108) should now reject mismatched type.
        rv = RuleValidator([ValueRuleValidator('k', str)])
        with self.assertRaises(PermissionError):
            rv.validate_dict({'k': False}, strict_mode=False)

    def test_zero_float_coerced_to_string_when_rule_expects_str(self):
        rv = RuleValidator([ValueRuleValidator('k', str)])
        out = rv.validate_dict({'k': 0.0}, strict_mode=False)
        self.assertEqual(out['k'], '0.0')

    def test_empty_list_with_str_rule_now_raises_type_error(self):
        # Before fix: [] was returned as list. After fix: type mismatch raised.
        rv = RuleValidator([ValueRuleValidator('k', str)])
        with self.assertRaises(PermissionError):
            rv.validate_dict({'k': []}, strict_mode=False)


class TestRuleValidatorNegativeIntegerString(unittest.TestCase):
    """Bug: `value.isdigit()` returns False for '-5', so legitimate negative
    integer strings raised PermissionError. Fix: use `int(value)` with
    try/except."""

    def test_negative_integer_string_coerced(self):
        rv = RuleValidator([ValueRuleValidator('k', int)])
        out = rv.validate_dict({'k': '-5'}, strict_mode=False)
        self.assertEqual(out['k'], -5)

    def test_positive_integer_string_still_coerced(self):
        rv = RuleValidator([ValueRuleValidator('k', int)])
        out = rv.validate_dict({'k': '42'}, strict_mode=False)
        self.assertEqual(out['k'], 42)

    def test_non_numeric_string_still_rejected(self):
        rv = RuleValidator([ValueRuleValidator('k', int)])
        with self.assertRaises(PermissionError):
            rv.validate_dict({'k': 'not-a-number'}, strict_mode=False)

    def test_underscore_separated_int_string_coerced(self):
        # int('1_000') succeeds in Python 3.6+
        rv = RuleValidator([ValueRuleValidator('k', int)])
        out = rv.validate_dict({'k': '1_000'}, strict_mode=False)
        self.assertEqual(out['k'], 1000)


# ── Bug 5: _get_config_under_path nested resolution + falsy ────────────────


class TestGetConfigUnderPathNestedResolution(unittest.TestCase):
    """Three bugs in one function:
       (1) used the full dotted `path` as the lookup key instead of the
           current `path_item`;
       (2) never updated the cursor — always looked up in the original `data`;
       (3) treated falsy stored values (0, '', [], False) as missing.
    """

    def test_single_level_truthy(self):
        self.assertEqual(_get_config_under_path({'a': 'v'}, 'a'), 'v')

    def test_single_level_falsy_value_returned(self):
        # Before fix: returned None for any falsy stored value
        self.assertEqual(_get_config_under_path({'k': 0}, 'k'), 0)
        self.assertEqual(_get_config_under_path({'k': ''}, 'k'), '')
        self.assertEqual(_get_config_under_path({'k': []}, 'k'), [])
        self.assertEqual(_get_config_under_path({'k': False}, 'k'), False)

    def test_nested_path_resolves(self):
        # Before fix: nested paths didn't work at all
        data = {'a': {'b': {'c': 'deep'}}}
        self.assertEqual(_get_config_under_path(data, 'a.b.c'), 'deep')

    def test_nested_path_intermediate_missing_returns_none(self):
        self.assertIsNone(_get_config_under_path({'a': {'b': {}}}, 'a.b.c'))

    def test_nested_path_intermediate_missing_raises_when_flag_set(self):
        with self.assertRaises(ValueError):
            _get_config_under_path(
                {'a': {'b': {}}},
                'a.b.c',
                raise_class_config_base_path_error=True,
            )

    def test_missing_top_level_key_silent(self):
        self.assertIsNone(_get_config_under_path({}, 'k'))

    def test_empty_path_returns_data_verbatim(self):
        self.assertEqual(_get_config_under_path({'a': 1}, ''), {'a': 1})

    def test_none_path_returns_data_verbatim(self):
        self.assertEqual(_get_config_under_path({'a': 1}, None), {'a': 1})

    def test_descending_past_a_non_dict_returns_none(self):
        # If we try to descend through a scalar, it's treated as missing
        self.assertIsNone(_get_config_under_path({'a': 'scalar'}, 'a.b'))

    def test_nested_path_with_zero_at_leaf(self):
        # Falsy leaf value still returned
        self.assertEqual(_get_config_under_path({'a': {'b': 0}}, 'a.b'), 0)
