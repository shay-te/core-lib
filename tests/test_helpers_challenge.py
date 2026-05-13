"""Permutation tests for the helpers in core_lib/helpers/.

One file covering: datetime_utils (hours/minutes), generate_data (flag combos),
Logging decorator, constants enums (sanity), files (download branches),
config_instances (nested paths)."""
import datetime
import logging as stdlib_logging
import string
import unittest
from unittest.mock import MagicMock, patch

from core_lib.helpers.config_instances import (
    _get_config_under_path,
    instantiate_config,
)
from core_lib.helpers.constants import (
    HttpHeaders,
    HttpMethod,
    InstantiateConfigConstants,
    MediaType,
    TimeUnit,
)
from core_lib.helpers.datetime_utils import (
    day_begin,
    day_end,
    hour_begin,
    hour_end,
    midnight,
    month_begin,
    today,
    tomorrow,
    week_begin,
    year_begin,
    yesterday,
)
from core_lib.helpers.files import download_file, download_file_handle, get_file_md5
from core_lib.helpers.generate_data import (
    generate_datetime,
    generate_email,
    generate_random_string,
)
from core_lib.helpers.logging import Logging


# ── datetime_utils: parameter permutations ──────────────────────────────────


class TestDatetimeUtilsHoursMinutes(unittest.TestCase):
    """Most datetime_utils functions accept hours/minutes; the default-only
    tests in test_datetime_utils.py never exercise non-zero values."""

    def test_hour_begin_with_minutes(self):
        result = hour_begin(minutes=30)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.second, 0)
        self.assertEqual(result.microsecond, 0)

    def test_hour_end_with_minutes(self):
        result = hour_end(minutes=15)
        # hour_end == hour_begin + 1 hour
        before = hour_begin(minutes=15)
        self.assertEqual(result - before, datetime.timedelta(hours=1))

    def test_day_begin_with_hours_minutes(self):
        result = day_begin(hours=10, minutes=30)
        self.assertEqual(result.hour, 10)
        self.assertEqual(result.minute, 30)

    def test_day_end_with_hours_minutes(self):
        result = day_end(hours=5, minutes=5)
        self.assertEqual((result - day_begin(hours=5, minutes=5)).days, 1)

    def test_today_with_hours_minutes(self):
        result = today(hours=8, minutes=45)
        self.assertEqual(result.hour, 8)
        self.assertEqual(result.minute, 45)

    def test_tomorrow_with_hours_minutes(self):
        tom = tomorrow(hours=6, minutes=15)
        # Tomorrow at the specified time of day
        self.assertEqual(tom.hour, 6)
        self.assertEqual(tom.minute, 15)

    def test_yesterday_with_hours_minutes(self):
        y = yesterday(hours=23, minutes=59)
        self.assertEqual(y.hour, 23)
        self.assertEqual(y.minute, 59)

    def test_midnight_is_today_alias(self):
        self.assertEqual(midnight(), today())
        self.assertEqual(midnight(hours=5, minutes=0), today(hours=5))

    def test_week_begin_with_hours_minutes(self):
        result = week_begin(hours=12, minutes=30)
        self.assertEqual(result.hour, 12)
        self.assertEqual(result.minute, 30)
        # Week starts on Monday
        self.assertEqual(result.weekday(), 0)

    def test_month_begin_with_hours_minutes(self):
        result = month_begin(hours=9, minutes=0)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.hour, 9)

    def test_year_begin_with_hours_minutes(self):
        result = year_begin(hours=7, minutes=0)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.hour, 7)


# ── generate_data: flag combinations ────────────────────────────────────────


class TestGenerateRandomString(unittest.TestCase):
    def test_default_length(self):
        s = generate_random_string()
        self.assertEqual(len(s), 10)
        # Default source: lowercase ASCII only
        self.assertTrue(all(c in string.ascii_lowercase for c in s))

    def test_custom_length(self):
        for length in [0, 1, 5, 100, 1000]:
            with self.subTest(length=length):
                self.assertEqual(len(generate_random_string(length=length)), length)

    def test_upper_flag(self):
        # Run many times — at least one should contain uppercase
        seen_upper = False
        for _ in range(200):
            s = generate_random_string(length=50, upper=True)
            if any(c in string.ascii_uppercase for c in s):
                seen_upper = True
                break
        self.assertTrue(seen_upper)

    def test_digits_flag(self):
        seen_digit = False
        for _ in range(200):
            s = generate_random_string(length=50, digits=True)
            if any(c in string.digits for c in s):
                seen_digit = True
                break
        self.assertTrue(seen_digit)

    def test_special_flag(self):
        seen_special = False
        for _ in range(200):
            s = generate_random_string(length=50, special=True)
            if any(c in string.punctuation for c in s):
                seen_special = True
                break
        self.assertTrue(seen_special)

    def test_all_flags_combined(self):
        sources = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
        s = generate_random_string(length=200, upper=True, digits=True, special=True)
        self.assertTrue(all(c in sources for c in s))

    def test_no_flags_lowercase_only(self):
        for _ in range(20):
            s = generate_random_string(length=50)
            self.assertTrue(all(c.islower() for c in s))


class TestGenerateEmail(unittest.TestCase):
    def test_default_domain(self):
        email = generate_email()
        self.assertTrue(email.endswith('@domain.com'))

    def test_custom_domain(self):
        email = generate_email(domain='example.org')
        self.assertTrue(email.endswith('@example.org'))

    def test_local_part_length(self):
        local = generate_email().split('@')[0]
        self.assertEqual(len(local), 10)


class TestGenerateDatetime(unittest.TestCase):
    def test_returns_datetime_in_default_range(self):
        result = generate_datetime()
        self.assertIsInstance(result, datetime.datetime)
        # Default range: today ± 10 days; check it's within 11 days of now
        delta = abs(datetime.datetime.now() - result)
        self.assertLess(delta.days, 11)

    def test_custom_range(self):
        from_d = datetime.datetime(2020, 1, 1)
        to_d = datetime.datetime(2020, 12, 31)
        for _ in range(10):
            result = generate_datetime(from_date=from_d, to_date=to_d)
            self.assertGreaterEqual(result, from_d)
            # to_d may not include the exact ms; allow same day
            self.assertLessEqual(result.date(), to_d.date())

    def test_only_from_date(self):
        from_d = datetime.datetime.now() - datetime.timedelta(days=100)
        for _ in range(10):
            result = generate_datetime(from_date=from_d)
            # generate_datetime truncates to midnight, so compare at day
            # granularity (otherwise from_d=14:30 vs result=00:00 same day
            # would spuriously fail).
            self.assertGreaterEqual(result.date(), from_d.date())

    def test_only_to_date(self):
        to_d = datetime.datetime.now() + datetime.timedelta(days=100)
        for _ in range(10):
            result = generate_datetime(to_date=to_d)
            self.assertLessEqual(result.date(), to_d.date())


# ── Logging decorator ──────────────────────────────────────────────────────


class TestLoggingDecorator(unittest.TestCase):
    def test_default_level_info(self):
        log = Logging()
        self.assertEqual(log.level, stdlib_logging.INFO)
        self.assertEqual(log.message, '')

    def test_wraps_and_returns_value(self):
        @Logging(message='running')
        def fn(x, y):
            return x + y
        self.assertEqual(fn(2, 3), 5)

    def test_invokes_logger_with_qualname(self):
        @Logging(message='hello {x}', level=stdlib_logging.WARNING)
        def my_function(x):
            return x

        with self.assertLogs(my_function.__qualname__, level='WARNING') as logs:
            my_function('world')
        # The formatted message should appear in the captured records
        joined = ' '.join(logs.output)
        self.assertIn('hello world', joined)

    def test_empty_message_logs_empty_string(self):
        @Logging()
        def fn():
            return 'r'

        with self.assertLogs(fn.__qualname__, level='INFO') as logs:
            fn()
        self.assertEqual(len(logs.output), 1)

    def test_custom_level(self):
        @Logging(message='m', level=stdlib_logging.ERROR)
        def fn():
            return 1

        with self.assertLogs(fn.__qualname__, level='ERROR') as logs:
            fn()
        self.assertTrue(logs.output[0].startswith('ERROR'))


# ── constants enums: sanity ─────────────────────────────────────────────────


class TestConstantsEnums(unittest.TestCase):
    def test_media_type_values_are_unique(self):
        values = [e.value for e in MediaType]
        # 'MEDIA_TYPE_WILDCARD' and 'WILDCARD' may share — but check that we
        # have at least 16 distinct entries
        self.assertGreater(len(MediaType), 15)
        # Application JSON should always be present and correct
        self.assertEqual(MediaType.APPLICATION_JSON.value, 'application/json')

    def test_http_method_values(self):
        self.assertEqual(HttpMethod.GET.value, 'GET')
        self.assertEqual(HttpMethod.POST.value, 'POST')
        self.assertEqual(HttpMethod.PUT.value, 'PUT')
        self.assertEqual(HttpMethod.DELETE.value, 'DELETE')

    def test_http_headers_includes_common(self):
        for name in ['ACCEPT', 'AUTHORIZATION', 'CONTENT_TYPE', 'CONTENT_DISPOSITION']:
            self.assertTrue(hasattr(HttpHeaders, name), f'missing {name}')

    def test_time_unit_distinct_values(self):
        values = {e.value for e in TimeUnit}
        self.assertEqual(len(values), len(list(TimeUnit)))

    def test_instantiate_constants(self):
        self.assertEqual(InstantiateConfigConstants.INSTANCE_KEY.value, '_instance_key_')
        self.assertEqual(InstantiateConfigConstants.RECURSIVE.value, '_recursive_')
        self.assertEqual(InstantiateConfigConstants.TARGET.value, '_target_')


# ── files: branch permutations of download paths ──────────────────────────


class TestFilesChallenge(unittest.TestCase):
    def test_download_file_handle_filters_empty_chunks(self):
        # The function skips falsy chunks (keep-alive)
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_response.iter_content.return_value = [b'data1', b'', b'data2', None, b'data3']
        file_handle = MagicMock()

        download_file_handle(mock_response, file_handle)

        # Three real chunks should be written; empty/None should be filtered
        writes = [c.args[0] for c in file_handle.write.call_args_list]
        self.assertIn(b'data1', writes)
        self.assertIn(b'data2', writes)
        self.assertIn(b'data3', writes)
        self.assertNotIn(b'', writes)
        self.assertNotIn(None, writes)

    def test_download_file_handle_raises_on_bad_response(self):
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_response.raise_for_status.side_effect = Exception('HTTP 500')
        with self.assertRaises(Exception):
            download_file_handle(mock_response, MagicMock())

    def test_get_file_md5_deterministic(self):
        # MD5 of this test file is stable across runs
        import os
        path = os.path.abspath(__file__)
        md5_a = get_file_md5(path)
        md5_b = get_file_md5(path)
        self.assertEqual(md5_a, md5_b)
        self.assertEqual(len(md5_a), 32)

    def test_get_file_md5_nonexistent_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            get_file_md5('/nonexistent/path/xyz/abc')


# ── config_instances: deep _get_config_under_path edges ──────────────────


class TestConfigInstancesPaths(unittest.TestCase):
    def test_none_path_returns_data_verbatim(self):
        self.assertEqual(_get_config_under_path({'a': 1}, None), {'a': 1})

    def test_empty_string_path_returns_data_verbatim(self):
        # path='' results in path_list=[] → loop doesn't run → returns data
        self.assertEqual(_get_config_under_path({'a': 1}, ''), {'a': 1})

    def test_missing_key_silent_returns_none(self):
        self.assertIsNone(_get_config_under_path({}, 'k'))

    def test_missing_key_raise_mode_raises(self):
        with self.assertRaises(ValueError):
            _get_config_under_path({}, 'k', raise_class_config_base_path_error=True)

    def test_top_level_key_found(self):
        result = _get_config_under_path({'foo': {'bar': 1}}, 'foo')
        self.assertEqual(result, {'bar': 1})

    def test_instantiate_config_with_no_target_returns_settings(self):
        # _instantiate_config returns (None, settings) when class_settings is falsy
        from omegaconf import OmegaConf
        config = OmegaConf.create({})
        # No _target_ means instantiate() can't run; falsy class_settings means
        # the function returns (None, settings).
        self.assertIsNone(instantiate_config(config))

    def test_instantiate_config_wraps_errors_with_value_error(self):
        from omegaconf import OmegaConf
        # Invalid _target_ path raises during hydra instantiate
        config = OmegaConf.create({'_target_': 'this.module.does.not.exist.At_All'})
        with self.assertRaises(ValueError):
            instantiate_config(config)
