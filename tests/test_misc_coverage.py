"""Fill remaining small coverage gaps across multiple modules."""
import logging
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from core_lib.helpers.config_instances import (
    instantiate_config_group_generator_dict,
    instantiate_config_group_generator_list,
    _get_config_under_path,
)
from core_lib.helpers.files import download_file, download_file_handle
from core_lib.helpers.func_utils import (
    Keyable,
    UnseenFormatter,
    _get_key_value,
    build_function_key,
)
from core_lib.observer.observer import Observer
from core_lib.observer.observer_listener import ObserverListener
from core_lib.registry.default_registry import DefaultRegistry
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


# ── config_instances ─────────────────────────────────────────────────────────


class TestConfigInstances(unittest.TestCase):
    def test_generator_dict(self):
        from omegaconf import OmegaConf

        conf = OmegaConf.create({'a': {}})
        results = list(instantiate_config_group_generator_dict(conf))
        self.assertEqual(len(results), 1)
        name, _instance, _settings = results[0]
        self.assertEqual(name, 'a')

    def test_generator_list(self):
        from omegaconf import OmegaConf

        conf = OmegaConf.create([{}])
        results = list(instantiate_config_group_generator_list(conf))
        self.assertEqual(len(results), 1)

    def test_get_config_under_path_returns_data_when_no_path(self):
        result = _get_config_under_path({'a': 1}, None)
        self.assertEqual(result, {'a': 1})

    def test_get_config_under_path_missing_raises(self):
        with self.assertRaises(ValueError):
            _get_config_under_path({}, 'missing', raise_class_config_base_path_error=True)

    def test_get_config_under_path_missing_silent(self):
        self.assertIsNone(_get_config_under_path({}, 'missing'))

    def test_get_config_under_path_finds_key(self):
        result = _get_config_under_path({'k': {'inner': 1}}, 'k')
        self.assertEqual(result, {'inner': 1})


# ── files ───────────────────────────────────────────────────────────────────


class TestFiles(unittest.TestCase):
    def test_download_file_handle_writes_chunks(self):
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_response.iter_content.return_value = [b'hello', b'', b'world']
        file_handle = MagicMock()
        download_file_handle(mock_response, file_handle)
        mock_response.raise_for_status.assert_called_once_with()
        file_handle.write.assert_any_call(b'hello')
        file_handle.write.assert_any_call(b'world')

    def test_download_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with patch('core_lib.helpers.files.requests.get') as mock_get:
                mock_get.return_value.__enter__.return_value = mock_get.return_value
                mock_get.return_value.iter_content.return_value = [b'data']
                download_file('http://example.com/x', tmp_path)
            with open(tmp_path, 'rb') as fh:
                self.assertEqual(fh.read(), b'data')
        finally:
            os.unlink(tmp_path)


# ── func_utils ──────────────────────────────────────────────────────────────


class _MyKey(Keyable):
    def key(self):
        return 'my-key'


class TestFuncUtils(unittest.TestCase):
    def test_get_key_value_with_keyable(self):
        self.assertEqual(_get_key_value('k', _MyKey()), 'my-key')

    def test_get_key_value_with_falsy(self):
        self.assertEqual(_get_key_value('k', None), '!EkE!')

    def test_unseen_formatter_missing_kwarg(self):
        f = UnseenFormatter()
        result = f.format('{foo}', bar='no')
        self.assertEqual(result, '!MfooM!')

    def test_unseen_formatter_keyable_value(self):
        f = UnseenFormatter()
        result = f.format('{key}', key=_MyKey())
        self.assertEqual(result, 'my-key')

    def test_unseen_formatter_exception_path(self):
        f = UnseenFormatter()
        class BadDict(dict):
            def __contains__(self, key):
                raise RuntimeError('boom')
        bd = BadDict()
        result = f.get_value('any', (), bd)
        self.assertEqual(result, '!EanyE!')

    def test_build_function_key_without_key_uses_qualname(self):
        def foo():
            pass  # intentionally empty
        self.assertEqual(build_function_key(None, foo), foo.__qualname__)


# ── observer ────────────────────────────────────────────────────────────────


class _Listener(ObserverListener):
    def __init__(self):
        self.last = None
        self.fail = False

    def update(self, key, value):
        if self.fail:
            raise RuntimeError('boom')
        self.last = (key, value)


class TestObserverCoverage(unittest.TestCase):
    def test_observer_with_initial_listener_and_detach(self):
        l = _Listener()
        obs = Observer(listener=l, listener_type=_Listener)
        obs.notify('k', 'v')
        self.assertEqual(l.last, ('k', 'v'))
        obs.detach(l)
        l2 = _Listener()
        obs.attach(l2)
        obs.notify('k2', 'v2')
        self.assertEqual(l2.last, ('k2', 'v2'))

    def test_observer_validate_assert(self):
        obs = Observer(listener_type=_Listener)
        with self.assertRaises(AssertionError):
            obs.attach(None)  # NOSONAR(python:S5655)

    def test_observer_validate_type(self):
        obs = Observer(listener_type=_Listener)
        with self.assertRaises(AssertionError):
            obs.attach('not-a-listener')

    def test_observer_notify_propagates_exception(self):
        bad = _Listener()
        bad.fail = True
        obs = Observer(listener=bad, listener_type=_Listener)
        observer_logger = logging.getLogger('core_lib.observer.observer')
        previous = observer_logger.disabled
        observer_logger.disabled = True
        try:
            with self.assertRaises(RuntimeError):
                obs.notify('k', 'v')
        finally:
            observer_logger.disabled = previous


# ── observer_decorator ──────────────────────────────────────────────────────


class TestObserverDecorator(unittest.TestCase):
    def test_observe_with_value_param_name_notify_after(self):
        from core_lib.observer.observer_decorator import Observe
        from core_lib.core_lib import CoreLib
        events = []

        class L(ObserverListener):
            def update(self, key, value):
                events.append((key, value))

        obs = Observer(listener_type=L)
        listener = L()
        obs.attach(listener)

        unique = '__test_observer_decorator__'
        CoreLib.observer_registry.register(unique, obs)
        try:
            @Observe(event_key='evt', value_param_name='x', observer_name=unique, notify_before=False)
            def my_func(x):
                return x * 2

            self.assertEqual(my_func(5), 10)
            self.assertEqual(events, [('evt', 5)])
        finally:
            CoreLib.observer_registry.unregister(unique)

    def test_observe_notify_before(self):
        from core_lib.observer.observer_decorator import Observe
        from core_lib.core_lib import CoreLib

        events = []

        class L(ObserverListener):
            def update(self, key, value):
                events.append((key, value))

        obs = Observer(listener_type=L)
        obs.attach(L())

        unique = '__test_observer_decorator_before__'
        CoreLib.observer_registry.register(unique, obs)
        try:
            @Observe(event_key='evt', observer_name=unique, notify_before=True)
            def my_func(x):
                return x

            my_func(7)
            self.assertEqual(events[0][0], 'evt')
            self.assertIn('x', events[0][1])
        finally:
            CoreLib.observer_registry.unregister(unique)


# ── default_registry ────────────────────────────────────────────────────────


class TestDefaultRegistry(unittest.TestCase):
    def test_constructor_requires_object_type(self):
        with self.assertRaises(ValueError):
            DefaultRegistry(None)

    def test_register_duplicate_raises(self):
        class A:
            pass  # intentionally empty
        r = DefaultRegistry(A)
        r.register('k', A())
        with self.assertRaises(ValueError):
            r.register('k', A())


# ── security_handler ───────────────────────────────────────────────────────


class _NoopUserSecurity(UserSecurity):
    def secure_entry(self, request, session_obj, policies):
        return None
    def from_session_data(self, session_data):
        return session_data
    def generate_session_data(self, obj):
        return obj


class TestSecurityHandler(unittest.TestCase):
    def test_register_double_raises(self):
        # SecurityHandler.user_security may already be set; reset for isolation
        original = SecurityHandler.user_security
        try:
            SecurityHandler.user_security = None
            handler = MagicMock()
            SecurityHandler.register(handler)
            with self.assertRaises(ValueError):
                SecurityHandler.register(handler)
        finally:
            SecurityHandler.user_security = original

    def test_get_raises_when_not_set(self):
        original = SecurityHandler.user_security
        try:
            SecurityHandler.user_security = None
            with self.assertRaises(ValueError):
                SecurityHandler.get()
        finally:
            SecurityHandler.user_security = original


# ── user_security ───────────────────────────────────────────────────────────


class TestUserSecurityCoverage(unittest.TestCase):
    def _make(self):
        token_handler = MagicMock()
        return _NoopUserSecurity('cookie', token_handler), token_handler

    def test_token_to_session_returns_session(self):
        us, th = self._make()
        th.decode.return_value = {'k': 1}
        self.assertEqual(us.token_to_session_object('tok'), {'k': 1})

    def test_token_to_session_returns_none_when_no_data(self):
        us, th = self._make()
        th.decode.return_value = None
        self.assertIsNone(us.token_to_session_object('tok'))

    def test_token_to_session_returns_none_on_exception(self):
        us, th = self._make()
        th.decode.side_effect = RuntimeError('boom')
        self.assertIsNone(us.token_to_session_object('tok'))


# ── web_helpers_utils ──────────────────────────────────────────────────────


class TestWebHelpersUtilsCoverage(unittest.TestCase):
    def test_get_server_type_when_not_initialized_raises(self):
        original = WebHelpersUtils.server_type
        try:
            WebHelpersUtils.server_type = None
            with self.assertRaises(ValueError):
                WebHelpersUtils.get_server_type()
        finally:
            WebHelpersUtils.server_type = original
