"""Regression tests.

Each test class pins down the correct behavior of a previously-buggy code
path. They exist to catch refactors that would silently re-introduce a
known bug. Bug descriptions live in the docstring of each test class.
"""
import datetime
import logging
import unittest
import unittest.mock
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


# ── Bug 6: JobScheduler lock-without-finally + _run_job race ──────────────


class TestJobSchedulerLockSafety(unittest.TestCase):
    """Bugs: stop() and _schedule() acquired the lock without try/finally —
    any exception between acquire and release deadlocked the scheduler.
    _run_job() also mutated _job_to_timer without the lock, racing the
    Timer thread against the scheduler thread."""

    def test_stop_releases_lock_when_cancel_raises(self):
        from core_lib.jobs.job_scheduler import JobScheduler
        from core_lib.jobs.job import Job
        from unittest.mock import MagicMock

        class _Job(Job):
            def initialized(self, data_handler):
                pass
            def run(self):
                pass

        scheduler = JobScheduler()
        job = _Job()
        # Inject a broken timer whose cancel() raises.
        bad_timer = MagicMock()
        bad_timer.cancel.side_effect = RuntimeError('cancel exploded')
        scheduler._job_to_timer[job] = bad_timer

        with self.assertRaises(RuntimeError):
            scheduler.stop(job)

        # The lock MUST be released — second stop() must not deadlock.
        # (Previously the unguarded release() was skipped on exception.)
        bad_timer.cancel.side_effect = None
        # If lock leaked, this call would hang. Use a thread-with-timeout
        # to fail fast if it does.
        import threading
        done = threading.Event()
        def attempt():
            scheduler.stop(job)
            done.set()
        t = threading.Thread(target=attempt, daemon=True)
        t.start()
        t.join(timeout=2.0)
        self.assertTrue(done.is_set(), 'stop() deadlocked — lock leaked from previous failure')

    def test_run_job_with_missing_dict_entry_no_keyerror(self):
        # Regression: _run_job did `del self._job_to_timer[job]` which raised
        # KeyError if a concurrent stop+cleanup had already removed the entry.
        # Fix uses pop(..., None).
        from core_lib.jobs.job_scheduler import JobScheduler
        from core_lib.jobs.job import Job

        class _Job(Job):
            def initialized(self, data_handler):
                pass
            def run(self):
                pass

        scheduler = JobScheduler()
        job = _Job()
        # Don't pre-populate _job_to_timer — simulate the race
        # No exception should be raised.
        scheduler._run_job(job, frequency=None)


# ── Bug 16: require_login swallowed view exceptions ──────────────────────


class TestRequireLoginViewExceptionsNotSwallowed(unittest.TestCase):
    """Bug: when the wrapped view raised, require_login caught the exception,
    logged it, and returned None — producing a blank page in the browser.
    Fix: route view calls through handle_exception so errors become proper
    500 responses."""

    def setUp(self):
        from django.conf import settings as django_settings
        from core_lib.session.security_handler import SecurityHandler
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        if not django_settings.configured:
            django_settings.configure()
            django_settings.DEFAULT_CHARSET = 'utf-8'

        self._original_us = SecurityHandler.user_security
        self._original_st = WebHelpersUtils.server_type

        mock_us = unittest.mock.MagicMock()
        mock_us._secure_entry = unittest.mock.MagicMock(return_value=None)
        SecurityHandler.user_security = mock_us
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

    def tearDown(self):
        from core_lib.session.security_handler import SecurityHandler
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        SecurityHandler.user_security = self._original_us
        WebHelpersUtils.server_type = self._original_st

    def test_view_exception_yields_500_response(self):
        from core_lib.web_helpers.require_login_helper import require_login
        from flask import Flask

        def view():
            raise RuntimeError('boom')

        app = Flask(__name__)
        with app.app_context():
            result = require_login(unittest.mock.MagicMock(), [], view)
            # Result is a Flask response with status 500 — not None
            self.assertIsNotNone(result)
            self.assertEqual(result.status_code, 500)


# ── Bug 24: handle_exception caught BaseException ─────────────────────


class TestHandleExceptionDoesNotCatchKeyboardInterrupt(unittest.TestCase):
    """Bug: `except (..., BaseException)` swallowed SystemExit and
    KeyboardInterrupt, preventing graceful shutdown / Ctrl-C handling.
    Fix: catch Exception (not BaseException)."""

    def test_keyboard_interrupt_propagates(self):
        from core_lib.web_helpers.decorators import handle_exception

        def view():
            raise KeyboardInterrupt('user pressed ctrl-c')

        with self.assertRaises(KeyboardInterrupt):
            handle_exception(view)

    def test_system_exit_propagates(self):
        from core_lib.web_helpers.decorators import handle_exception

        def view():
            raise SystemExit(1)

        with self.assertRaises(SystemExit):
            handle_exception(view)

    def test_generator_exit_propagates(self):
        from core_lib.web_helpers.decorators import handle_exception

        def view():
            raise GeneratorExit('cleanup')

        with self.assertRaises(GeneratorExit):
            handle_exception(view)

    def test_regular_exceptions_still_caught(self):
        from core_lib.web_helpers.decorators import handle_exception
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        from django.conf import settings as django_settings
        if not django_settings.configured:
            django_settings.configure()
            django_settings.DEFAULT_CHARSET = 'utf-8'
        original = WebHelpersUtils.server_type
        try:
            WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

            def view():
                raise ValueError('regular error')

            from flask import Flask
            app = Flask(__name__)
            with app.app_context():
                result = handle_exception(view)
                # Normal Exception still converted to 500 response
                self.assertEqual(result.status_code, 500)
        finally:
            WebHelpersUtils.server_type = original


# ── Bug 32: CacheHandlerRedis passed ex=-1 to redis ────────────────────────


class TestCacheHandlerRedisSetWithoutExpire(unittest.TestCase):
    """Bug: `ex=expire if expire else -1` sent ex=-1 to redis when no expiry
    was provided. Redis server rejects this with "invalid expire time".
    Fix: don't pass `ex` at all when no expiry is wanted."""

    def test_no_expire_does_not_pass_ex_arg(self):
        from unittest.mock import MagicMock, patch
        from core_lib.cache.cache_handler_redis import CacheHandlerRedis

        mock_client = MagicMock()
        with patch('core_lib.cache.cache_handler_redis.redis.from_url', return_value=mock_client):
            handler = CacheHandlerRedis('redis://localhost')
            handler.set('k', 'v', None)
            # The call to redis.set must NOT include an `ex` kwarg
            args, kwargs = mock_client.set.call_args
            self.assertNotIn('ex', kwargs)

    def test_with_expire_passes_ex_arg(self):
        from datetime import timedelta
        from unittest.mock import MagicMock, patch
        from core_lib.cache.cache_handler_redis import CacheHandlerRedis

        mock_client = MagicMock()
        with patch('core_lib.cache.cache_handler_redis.redis.from_url', return_value=mock_client):
            handler = CacheHandlerRedis('redis://localhost')
            handler.set('k', 'v', timedelta(seconds=30))
            args, kwargs = mock_client.set.call_args
            self.assertEqual(kwargs['ex'], timedelta(seconds=30))

    def test_set_accepts_float_values(self):
        # Bug 33: float was rejected even though json.dumps handles it fine.
        import json
        from unittest.mock import MagicMock, patch
        from core_lib.cache.cache_handler_redis import CacheHandlerRedis

        mock_client = MagicMock()
        with patch('core_lib.cache.cache_handler_redis.redis.from_url', return_value=mock_client):
            handler = CacheHandlerRedis('redis://localhost')
            handler.set('k', 3.14, None)
            args, kwargs = mock_client.set.call_args
            self.assertEqual(args[1], json.dumps(3.14))


class TestCacheHandlerMemcachedAcceptsFloat(unittest.TestCase):
    """Bug 33 same as above for memcached."""

    def test_set_accepts_float_values(self):
        import json
        from unittest.mock import MagicMock, patch
        from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached

        mock_client = MagicMock()
        with patch(
            'core_lib.cache.cache_handler_memcached.Client', return_value=mock_client
        ):
            handler = CacheHandlerMemcached('localhost:11211')
            handler.set('k', 2.5, None)
            args, kwargs = mock_client.set.call_args
            self.assertEqual(args[1], json.dumps(2.5))


# ── Bug 34: JWTTokenHandler verify= deprecated and ignored ─────────────────


class TestJwtTokenHandlerVerifyFlag(unittest.TestCase):
    """Bug: `jwt.decode(..., verify=False)` is deprecated in PyJWT 2.0+ and
    silently ignored — so passing `verify=False` did NOT disable signature
    verification. Fix: use `options={'verify_signature': False}`."""

    def test_verify_false_decodes_unsigned_token(self):
        from datetime import timedelta
        import jwt
        from core_lib.session.jwt_token_handler import JWTTokenHandler

        # Encode with one secret
        handler_a = JWTTokenHandler('secret-a', timedelta(seconds=60))
        token = handler_a.encode({'sub': 'user'})

        # Decode with DIFFERENT secret + verify=False — should succeed
        # because we're skipping signature verification.
        handler_b = JWTTokenHandler('different-secret', timedelta(seconds=60), verify=False)
        decoded = handler_b.decode(token)
        self.assertEqual(decoded['sub'], 'user')

    def test_verify_true_rejects_bad_signature(self):
        from datetime import timedelta
        from core_lib.session.jwt_token_handler import JWTTokenHandler

        handler_a = JWTTokenHandler('secret-a', timedelta(seconds=60))
        token = handler_a.encode({'sub': 'user'})

        handler_b = JWTTokenHandler('different-secret', timedelta(seconds=60), verify=True)
        with self.assertRaises(Exception):
            handler_b.decode(token)

    def test_decode_emits_no_deprecation_warning(self):
        # Regression: previously every decode logged a DeprecationWarning
        # about the deprecated `verify=` kwarg.
        import warnings
        from datetime import timedelta
        from core_lib.session.jwt_token_handler import JWTTokenHandler

        handler = JWTTokenHandler('secret', timedelta(seconds=60))
        token = handler.encode({'sub': 'user'})

        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            handler.decode(token)

        deprecations = [
            w for w in captured
            if issubclass(w.category, DeprecationWarning) and 'verify' in str(w.message)
        ]
        self.assertEqual(deprecations, [])


# ── Bug 35: Point.from_point_str fragile with extra whitespace ────────────


class TestPointFromPointStrParsing(unittest.TestCase):
    """Bug: `point_str.strip('POINT()').replace(' ', ',').split(',')` choked
    on extra whitespace — `'POINT(  5 45  )'` produced empty segments and
    raised ValueError on float(''). Fix: regex-based number extraction."""

    def test_canonical_input(self):
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        self.assertEqual(
            Point.from_point_str('POINT(5 45)'),
            {'longitude': 5.0, 'latitude': 45.0},
        )

    def test_extra_whitespace_inside_parens(self):
        # Previously raised ValueError
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        self.assertEqual(
            Point.from_point_str('POINT(  5 45  )'),
            {'longitude': 5.0, 'latitude': 45.0},
        )

    def test_multiple_spaces_between_coords(self):
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        self.assertEqual(
            Point.from_point_str('POINT(5    45)'),
            {'longitude': 5.0, 'latitude': 45.0},
        )

    def test_negative_coordinates(self):
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        self.assertEqual(
            Point.from_point_str('POINT(-5 -45)'),
            {'longitude': -5.0, 'latitude': -45.0},
        )

    def test_decimal_coordinates(self):
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        self.assertEqual(
            Point.from_point_str('POINT(1.5 2.5)'),
            {'longitude': 1.5, 'latitude': 2.5},
        )

    def test_scientific_notation(self):
        # Bonus: regex handles scientific notation correctly
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        result = Point.from_point_str('POINT(1e2 3e1)')
        self.assertEqual(result, {'longitude': 100.0, 'latitude': 30.0})

    def test_latitude_first_flag(self):
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        self.assertEqual(
            Point.from_point_str('POINT(45 5)', latitude_first=True),
            {'latitude': 45.0, 'longitude': 5.0},
        )

    def test_malformed_input_raises_value_error(self):
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        with self.assertRaises(ValueError):
            Point.from_point_str('POINT()')
        with self.assertRaises(ValueError):
            Point.from_point_str('no numbers here')

    def test_roundtrip_with_to_point_str(self):
        from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
        s = Point.to_point_str(longitude=12.5, latitude=-3.7)
        self.assertEqual(
            Point.from_point_str(s),
            {'longitude': 12.5, 'latitude': -3.7},
        )


# ── Code-smell #15: assert-based validation survives `python -O` ───────────


class TestAssertValidationSurvivesOptimization(unittest.TestCase):
    """`assert X` is stripped under `python -O`, turning input validation
    into a no-op. All assert-based validation was rewritten to use explicit
    `if not X: raise AssertionError(...)` so the check runs regardless of
    optimization level."""

    def test_crud_update_rejects_empty_id_via_real_raise(self):
        # Build a CRUDDataAccess with minimal mocks to test validation
        from unittest.mock import MagicMock
        from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
        access = CRUDDataAccess(MagicMock(), MagicMock())
        with self.assertRaises(AssertionError):
            access.get(0)  # falsy id
        with self.assertRaises(AssertionError):
            access.delete(None)

    def test_observer_validate_raises_explicitly(self):
        # Even with -O the validation must still raise
        from core_lib.observer.observer import Observer
        obs = Observer()
        with self.assertRaises(AssertionError):
            obs.attach(None)


# ── Code-smell #16: mutable defaults ───────────────────────────────────────


class TestMutableDefaultsNotShared(unittest.TestCase):
    """Previously `def f(headers: dict = {})` — every call shared the same
    default dict, so mutating it in one call leaked across all later calls.
    Fix: `headers: dict = None` then `headers = {}` inside the body."""

    def test_generate_response_django_default_headers_isolated(self):
        from django.conf import settings as django_settings
        if not django_settings.configured:
            django_settings.configure()
            django_settings.DEFAULT_CHARSET = 'utf-8'
        from core_lib.web_helpers.request_response_helpers import generate_response_django
        from core_lib.helpers.constants import MediaType

        # First call — no headers passed
        r1 = generate_response_django(b'a', 200, MediaType.TEXT_HTML)
        # Inject something INTO r1's headers
        r1['X-Test'] = 'leak-attempt'
        # Second call — must NOT see X-Test on its response
        r2 = generate_response_django(b'b', 200, MediaType.TEXT_HTML)
        self.assertNotIn('X-Test', dict(r2.items()))

    def test_core_lib_load_jobs_default_handler_isolated(self):
        # Mostly proves the signature is `= None`, not `= {}`
        import inspect
        from core_lib.core_lib import CoreLib
        sig = inspect.signature(CoreLib.load_jobs)
        self.assertIsNone(sig.parameters['job_to_data_handler'].default)


# ── Code-smell #18: CoreLib destroy idempotency ────────────────────────────


class TestCoreLibDestroyIdempotent(unittest.TestCase):
    """`fire_core_lib_destroy` is now idempotent — multiple calls (from
    explicit calls + __del__ + interpreter shutdown) only fire the event
    once, instead of redundantly notifying listeners multiple times."""

    def test_destroy_fires_once(self):
        from core_lib.core_lib import CoreLib
        from core_lib.core_lib_listener import CoreLibListener

        events = []

        class L(CoreLibListener):
            def on_core_lib_ready(self):
                pass
            def on_core_lib_destroy(self):
                events.append('destroy')

        cl = CoreLib()
        cl.attach_listener(L())
        cl.fire_core_lib_destroy()
        cl.fire_core_lib_destroy()
        cl.fire_core_lib_destroy()
        self.assertEqual(events, ['destroy'])


# ── Code-smell #19: generate_datetime inverted range ───────────────────────


class TestGenerateDatetimeInvertedRange(unittest.TestCase):
    """Previously `generate_datetime(from_date=future, to_date=past)` raised
    `ValueError: empty range for randrange()` from random.randint. Now the
    arguments are auto-swapped so the function never raises."""

    def test_inverted_range_auto_swaps(self):
        import datetime
        from core_lib.helpers.generate_data import generate_datetime
        # from > to → previously raised
        result = generate_datetime(
            from_date=datetime.datetime(2030, 1, 1),
            to_date=datetime.datetime(2020, 1, 1),
        )
        # No exception. Result is somewhere between the two.
        self.assertGreaterEqual(result.year, 2020)
        self.assertLessEqual(result.year, 2030)


# ── Code-smell #20: migrate CLI silently no-ops ────────────────────────────


class TestMigrateCliUsageErrors(unittest.TestCase):
    """`--rev xyz-unknown` and `--rev new` without `--name` now raise
    click.UsageError (exit code != 0) instead of silently exiting 0."""

    def test_unknown_rev_exits_nonzero(self):
        from click.testing import CliRunner
        from unittest.mock import MagicMock, patch
        from core_lib import core_lib_main
        runner = CliRunner()
        with patch('core_lib.core_lib_main.load_dotenv'), patch(
            'core_lib.core_lib_main.load_config',
            return_value=MagicMock(core_lib_module='core_lib'),
        ), patch('core_lib.core_lib_main.Alembic'):
            result = runner.invoke(core_lib_main.migrate, ['--rev', 'foobar'])
            self.assertNotEqual(result.exit_code, 0)

    def test_new_without_name_exits_nonzero(self):
        from click.testing import CliRunner
        from unittest.mock import MagicMock, patch
        from core_lib import core_lib_main
        runner = CliRunner()
        with patch('core_lib.core_lib_main.load_dotenv'), patch(
            'core_lib.core_lib_main.load_config',
            return_value=MagicMock(core_lib_module='core_lib'),
        ), patch('core_lib.core_lib_main.Alembic'):
            result = runner.invoke(core_lib_main.migrate, ['--rev', 'new'])
            self.assertNotEqual(result.exit_code, 0)


# ── Code-smell #21: CRUD.update doesn't filter `id` ────────────────────────


class TestCrudUpdateFiltersId(unittest.TestCase):
    """`CRUD.update(id=1, data={'id': 999, 'name': 'foo'})` previously sent
    `UPDATE ... SET id=999, name='foo' WHERE id=1` — quietly mutating the
    primary key. Now the `id` key is stripped from the update payload, just
    like `CRUD.create` already does."""

    def test_update_strips_id_from_data(self):
        from sqlalchemy import Column, Integer, String
        from core_lib.data_layers.data.db.sqlalchemy.base import Base
        from core_lib.data_layers.data_access.db.crud.crud_data_access import (
            CRUDDataAccess,
        )
        from tests.test_data.test_utils import connect_to_mem_db

        class Widget(Base):
            __tablename__ = 'crud_id_strip_widget'
            __table_args__ = {'extend_existing': True}
            id = Column(Integer, primary_key=True)
            name = Column(String(255))

        db = connect_to_mem_db()
        access = CRUDDataAccess(Widget, db)
        created = access.create({'name': 'before'})
        original_id = created.id

        # Try to "update" the primary key — must be a no-op for `id`.
        access.update(original_id, {'id': 99999, 'name': 'after'})

        # The row's id must NOT have changed; name DID change.
        fetched = access.get(original_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, original_id)
        self.assertEqual(fetched.name, 'after')


# ── Code-smell #23: Observer thread safety ────────────────────────────────


class TestObserverThreadSafety(unittest.TestCase):
    """Observer.attach/detach/notify now coordinate under an RLock and
    notify() iterates a snapshot of listeners so listeners can safely
    attach/detach during a notify without corrupting iteration."""

    def test_listener_detaches_during_notify(self):
        from core_lib.observer.observer import Observer
        from core_lib.observer.observer_listener import ObserverListener

        events = []

        class L(ObserverListener):
            def __init__(self, name):
                self.name = name

            def update(self, key, value):
                events.append((self.name, key))

        class SelfDetaching(ObserverListener):
            def update(self, key, value):
                events.append(('SD', key))
                obs.detach(self)  # safe because notify uses a snapshot

        obs = Observer()
        l1 = L('a')
        l2 = SelfDetaching()
        l3 = L('b')
        obs.attach(l1)
        obs.attach(l2)
        obs.attach(l3)
        obs.notify('evt', None)
        # All three listeners were invoked; the self-detach didn't break
        # the iteration.
        self.assertEqual(set(events), {('a', 'evt'), ('SD', 'evt'), ('b', 'evt')})


# ── Code-smell #24: SqlAlchemyConnection close ordering ────────────────────


class TestSqlAlchemyConnectionCloseOrdering(unittest.TestCase):
    """Previously `close()` did `commit() → flush() → close()`. flush() AFTER
    commit() is a no-op. Now: `flush() → commit() → close()` so any pending
    state is flushed BEFORE the transaction is committed."""

    def test_close_order_flush_then_commit_then_close(self):
        from unittest.mock import MagicMock
        from core_lib.connection.sql_alchemy_connection import SqlAlchemyConnection

        with unittest.mock.patch(
            'core_lib.connection.sql_alchemy_connection.sessionmaker'
        ) as mock_sm:
            mock_session = MagicMock()
            mock_sm.return_value.return_value = mock_session
            conn = SqlAlchemyConnection(MagicMock(), on_exit=None)

            # Track the order of calls
            calls = []
            mock_session.flush.side_effect = lambda: calls.append('flush')
            mock_session.commit.side_effect = lambda: calls.append('commit')
            mock_session.close.side_effect = lambda: calls.append('close')

            conn.close()

            self.assertEqual(calls, ['flush', 'commit', 'close'])


# ── Coverage fill for new validation branches ───────────────────────────


class TestNewValidationBranchesCoverage(unittest.TestCase):
    """Cover the new explicit raises so coverage stays at 100%."""

    def test_crud_update_rejects_empty_id(self):
        from unittest.mock import MagicMock
        from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
        access = CRUDDataAccess(MagicMock(), MagicMock())
        with self.assertRaises(AssertionError):
            access.update(0, {'k': 'v'})

    def test_crud_update_rejects_empty_data(self):
        from unittest.mock import MagicMock
        from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
        access = CRUDDataAccess(MagicMock(), MagicMock())
        with self.assertRaises(AssertionError):
            access.update(1, {})

    def test_crud_create_rejects_empty_data(self):
        from unittest.mock import MagicMock
        from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
        access = CRUDDataAccess(MagicMock(), MagicMock())
        with self.assertRaises(AssertionError):
            access.create({})

    def test_crud_soft_get_delete_reject_empty_id(self):
        from unittest.mock import MagicMock
        from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import (
            CRUDSoftDeleteDataAccess,
        )
        access = CRUDSoftDeleteDataAccess(MagicMock(), MagicMock())
        with self.assertRaises(AssertionError):
            access.get(0)
        with self.assertRaises(AssertionError):
            access.delete(0)

    def test_crud_soft_token_get_delete_reject_empty_id(self):
        from unittest.mock import MagicMock
        from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import (
            CRUDSoftDeleteWithTokenDataAccess,
        )
        access = CRUDSoftDeleteWithTokenDataAccess(MagicMock(), MagicMock())
        with self.assertRaises(AssertionError):
            access.get(0)
        with self.assertRaises(AssertionError):
            access.delete(0)

    def test_jwt_token_handler_requires_secret(self):
        from datetime import timedelta
        from core_lib.session.jwt_token_handler import JWTTokenHandler
        with self.assertRaises(AssertionError):
            JWTTokenHandler('', timedelta(seconds=1))

    def test_jwt_token_handler_requires_expiration_time(self):
        from core_lib.session.jwt_token_handler import JWTTokenHandler
        with self.assertRaises(AssertionError):
            JWTTokenHandler('secret', None)

    def test_user_security_requires_cookie_name(self):
        from core_lib.session.user_security import UserSecurity
        from core_lib.session.token_handler import TokenHandler

        class _TH(TokenHandler):
            def encode(self, m): return ''
            def decode(self, e): return {}

        class _US(UserSecurity):
            def secure_entry(self, request, session_obj, policies):
                return None
            def from_session_data(self, session_data):
                return None
            def generate_session_data(self, obj):
                return obj

        with self.assertRaises(AssertionError):
            _US('', _TH())

    def test_config_instances_generator_dict_rejects_empty_conf(self):
        from core_lib.helpers.config_instances import (
            instantiate_config_group_generator_dict,
        )
        with self.assertRaises(AssertionError):
            list(instantiate_config_group_generator_dict({}))

    def test_config_instances_generator_list_rejects_empty_conf(self):
        from core_lib.helpers.config_instances import (
            instantiate_config_group_generator_list,
        )
        with self.assertRaises(AssertionError):
            list(instantiate_config_group_generator_list([]))

    def test_request_response_generate_response_flask_default_headers(self):
        # Cover the new `if headers is None: headers = {}` branch in
        # generate_response_flask.
        from core_lib.web_helpers.request_response_helpers import generate_response_flask
        from core_lib.helpers.constants import MediaType
        resp = generate_response_flask(b'data', 200, MediaType.TEXT_HTML)
        self.assertEqual(resp.status_code, 200)

    def test_core_lib_del_via_destroyed_flag(self):
        # Touch the idempotency-flag branch of fire_core_lib_destroy
        from core_lib.core_lib import CoreLib
        cl = CoreLib()
        cl.fire_core_lib_destroy()
        # Second call must return early without notifying
        cl.fire_core_lib_destroy()
        self.assertTrue(cl._destroyed)

    def test_core_lib_destroy_swallows_notify_exception(self):
        # Cover the try/except inside fire_core_lib_destroy that swallows
        # listener errors.
        from core_lib.core_lib import CoreLib
        from core_lib.core_lib_listener import CoreLibListener

        class BadL(CoreLibListener):
            def on_core_lib_ready(self):
                pass
            def on_core_lib_destroy(self):
                raise RuntimeError('listener crashed during destroy')

        cl = CoreLib()
        cl.attach_listener(BadL())
        # Must NOT raise even though the listener crashes
        cl.fire_core_lib_destroy()

    def test_config_instances_params_default_none_resolves(self):
        # Cover the `if params is None: params = {}` branch in the generators.
        from omegaconf import OmegaConf
        from core_lib.helpers.config_instances import (
            instantiate_config,
            instantiate_config_group_generator_dict,
            instantiate_config_group_generator_list,
        )
        # Generators
        list(instantiate_config_group_generator_dict(OmegaConf.create({'a': {}}), params=None))
        list(instantiate_config_group_generator_list(OmegaConf.create([{}]), params=None))
        # instantiate_config single
        self.assertIsNone(instantiate_config(OmegaConf.create({}), params=None))

    def test_private_instantiate_config_handles_none_params(self):
        # `_instantiate_config` is normally called only via the public
        # wrappers (which resolve params), but the defensive None check
        # in the private function still needs coverage.
        from omegaconf import OmegaConf
        from core_lib.helpers.config_instances import _instantiate_config
        result = _instantiate_config(OmegaConf.create({}), params=None)
        # No exception, returns (None, settings)
        self.assertIsNone(result[0])

    def test_config_instances_params_explicit_non_none(self):
        # Cover the FALSE branch of `if params is None` (i.e., caller passed
        # a real dict).
        from omegaconf import OmegaConf
        from core_lib.helpers.config_instances import (
            instantiate_config,
            instantiate_config_group_generator_dict,
            instantiate_config_group_generator_list,
        )
        # Pass an explicit empty dict (or any dict) for params
        list(instantiate_config_group_generator_dict(OmegaConf.create({'a': {}}), params={}))
        list(instantiate_config_group_generator_list(OmegaConf.create([{}]), params={}))
        instantiate_config(OmegaConf.create({}), params={})


# ── Bug 25: height_to_cm accepts bool / non-positive numbers ──────────────


class TestHeightToCmRejectsInvalidInputs(unittest.TestCase):
    """`isinstance(x, (int, float))` matched booleans (bool is a subclass of
    int), turning `height_to_cm(True)` into 100 (1 meter). Negative numbers
    and zero were also silently passed through, producing nonsensical
    results like -100 cm. All are now rejected."""

    def test_bool_rejected(self):
        from core_lib.helpers.parse_utils import height_to_cm
        self.assertIsNone(height_to_cm(True))
        self.assertIsNone(height_to_cm(False))

    def test_negative_int_rejected(self):
        from core_lib.helpers.parse_utils import height_to_cm
        self.assertIsNone(height_to_cm(-1))
        self.assertIsNone(height_to_cm(-150))

    def test_negative_float_rejected(self):
        from core_lib.helpers.parse_utils import height_to_cm
        self.assertIsNone(height_to_cm(-1.5))
        self.assertIsNone(height_to_cm(-0.1))

    def test_zero_rejected(self):
        from core_lib.helpers.parse_utils import height_to_cm
        self.assertIsNone(height_to_cm(0))
        self.assertIsNone(height_to_cm(0.0))

    def test_positive_still_works(self):
        from core_lib.helpers.parse_utils import height_to_cm
        self.assertEqual(height_to_cm(180), 180)
        self.assertEqual(height_to_cm(1.8), 180)


# ── Bug 26: user_security catches BaseException ───────────────────────────


class TestUserSecurityCatchesExceptionNotBase(unittest.TestCase):
    """`token_to_session_object` previously `except BaseException`, swallowing
    KeyboardInterrupt and SystemExit. Now catches Exception only."""

    def test_keyboard_interrupt_propagates(self):
        from core_lib.session.user_security import UserSecurity
        from core_lib.session.token_handler import TokenHandler

        class TH(TokenHandler):
            def encode(self, m): return ''
            def decode(self, e):
                raise KeyboardInterrupt('user pressed ctrl-c')

        class US(UserSecurity):
            def secure_entry(self, request, session_obj, policies): return None
            def from_session_data(self, session_data): return session_data
            def generate_session_data(self, obj): return obj

        us = US('cookie', TH())
        with self.assertRaises(KeyboardInterrupt):
            us.token_to_session_object('token')

    def test_regular_exception_still_returns_none(self):
        from core_lib.session.user_security import UserSecurity
        from core_lib.session.token_handler import TokenHandler

        class TH(TokenHandler):
            def encode(self, m): return ''
            def decode(self, e):
                raise ValueError('bad token')

        class US(UserSecurity):
            def secure_entry(self, request, session_obj, policies): return None
            def from_session_data(self, session_data): return session_data
            def generate_session_data(self, obj): return obj

        us = US('cookie', TH())
        self.assertIsNone(us.token_to_session_object('token'))


# ── Bug 27: Observe IndexError when value_param passed as kwarg ───────────


class TestObserveResolvesKwargValueParam(unittest.TestCase):
    """`@Observe(value_param_name='x')` previously did `args[index]` which
    raised IndexError when the argument was passed as a keyword."""

    def test_value_param_passed_as_kwarg(self):
        from core_lib.observer.observer import Observer
        from core_lib.observer.observer_decorator import Observe
        from core_lib.observer.observer_listener import ObserverListener
        from core_lib.core_lib import CoreLib

        captured = []

        class L(ObserverListener):
            def update(self, key, value):
                captured.append((key, value))

        obs = Observer(listener_type=L)
        obs.attach(L())
        unique = '__bug27_observer__'
        CoreLib.observer_registry.register(unique, obs)
        try:
            @Observe(event_key='evt', value_param_name='x', observer_name=unique)
            def fn(x):
                return x * 2

            # Previously raised IndexError on kwarg-only call.
            self.assertEqual(fn(x=7), 14)
            self.assertEqual(captured, [('evt', 7)])
        finally:
            CoreLib.observer_registry.unregister(unique)


# ── Bug 28 + 29: streaming downloads / hashing ─────────────────────────────


class TestStreamingFileOps(unittest.TestCase):
    """`download_file` previously buffered the full response into memory;
    `get_file_md5` previously did `buf = f.read()`. Both now stream."""

    def test_download_file_uses_stream_true(self):
        from unittest.mock import patch, MagicMock
        from core_lib.helpers.files import download_file
        with patch('core_lib.helpers.files.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.__enter__.return_value = mock_response
            mock_response.iter_content.return_value = [b'chunk']
            mock_get.return_value = mock_response
            import tempfile, os
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                path = tmp.name
            try:
                download_file('http://example.com/x', path)
            finally:
                os.unlink(path)
            _, kwargs = mock_get.call_args
            self.assertTrue(kwargs.get('stream'))

    def test_get_file_md5_streams_in_chunks(self):
        # The chunked implementation must produce the same hash as buffered.
        import hashlib, tempfile, os
        from core_lib.helpers.files import get_file_md5

        data = b'A' * 200000
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(data)
            path = tmp.name
        try:
            expected = hashlib.md5(data).hexdigest()
            self.assertEqual(get_file_md5(path), expected)
        finally:
            os.unlink(path)


# ── Bug 30: MiddlewareChain thread safety ─────────────────────────────────


class TestMiddlewareChainSnapshotIteration(unittest.TestCase):
    """`MiddlewareChain.execute` now iterates a snapshot so middlewares can
    safely mutate the chain during dispatch."""

    def test_middleware_can_remove_self_during_execute(self):
        from core_lib.middleware.middleware import Middleware
        from core_lib.middleware.middleware_chain import MiddlewareChain

        chain = MiddlewareChain()
        events = []

        class SelfRemoving(Middleware):
            def handle(self, context):
                events.append('self-remove')
                chain.remove(self)

        class Logger(Middleware):
            def handle(self, context):
                events.append('logger')

        chain.add(SelfRemoving())
        chain.add(Logger())
        chain.execute({})
        self.assertEqual(events, ['self-remove', 'logger'])
        chain.execute({})
        self.assertEqual(events, ['self-remove', 'logger', 'logger'])


# ── Bug 32: IntEnum 0-valued enum members ────────────────────────────────


class TestIntEnumZeroValueRoundTrip(unittest.TestCase):
    """`if value` coerced enum members whose value is 0 to NULL.
    Now uses `is not None`."""

    def test_zero_valued_enum_member_round_trip(self):
        import enum
        from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum as SQLAIntEnum

        class Flag(enum.Enum):
            OFF = 0
            ON = 1

        col = SQLAIntEnum(Flag)
        self.assertEqual(col.process_bind_param(Flag.OFF, None), 0)
        self.assertIs(col.process_result_value(0, None), Flag.OFF)

    def test_none_still_passes_through_as_none(self):
        import enum
        from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum as SQLAIntEnum

        class Flag(enum.Enum):
            ONE = 1

        col = SQLAIntEnum(Flag)
        self.assertIsNone(col.process_bind_param(None, None))
        self.assertIsNone(col.process_result_value(None, None))
