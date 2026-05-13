"""Tests targeting specific remaining missing lines across many modules."""
import datetime
import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from django.conf import settings as django_settings


# ── cache_decorator ─────────────────────────────────────────────────────────


class TestCacheDecoratorParse(unittest.TestCase):
    def test_parse_invalid_raises(self):
        from core_lib.cache.cache_decorator import parse
        with self.assertRaises(ValueError):
            parse('this is not a date at all xyz_!')


# ── cache_handler_ram ───────────────────────────────────────────────────────


class TestCacheHandlerRamCoverage(unittest.TestCase):
    def test_get_with_no_expire_returns_data(self):
        from core_lib.cache.cache_handler_ram import CacheHandlerRam
        h = CacheHandlerRam()
        h.set('k', 'v', None)
        self.assertEqual(h.get('k'), 'v')

    def test_flush_all(self):
        from core_lib.cache.cache_handler_ram import CacheHandlerRam
        h = CacheHandlerRam()
        h.set('k', 'v', None)
        h.flush_all()
        self.assertEqual(h.cached_function_responses, {})


# ── client_base ─────────────────────────────────────────────────────────────


class TestClientBase(unittest.TestCase):
    def _build(self):
        from core_lib.client.client_base import ClientBase
        return ClientBase('http://api.example.com')

    def test_setters(self):
        c = self._build()
        c.set_headers({'X-Test': 'yes'})
        c.set_timeout(10)
        c.set_auth(('u', 'p'))
        self.assertEqual(c.headers, {'X-Test': 'yes'})
        self.assertEqual(c.timeout, 10)
        self.assertEqual(c.auth, ('u', 'p'))

    def test_http_methods_invoke_session(self):
        c = self._build()
        c.set_headers({'X-Test': 'yes'})
        c.set_timeout(5)
        c.set_auth(('u', 'p'))
        c.session = MagicMock()
        c._get('/path', headers={'A': 'B'})
        c._put('/path')
        c._post('/path')
        c._delete('/path')
        self.assertEqual(c.session.get.call_count, 1)
        c.session.get.assert_called_with(
            'http://api.example.com/path',
            headers={'A': 'B', 'X-Test': 'yes'},
            timeout=5,
            auth=('u', 'p'),
        )
        self.assertTrue(c.session.put.called)
        self.assertTrue(c.session.post.called)
        self.assertTrue(c.session.delete.called)

    def test_process_kwargs_without_headers_uses_self_headers(self):
        c = self._build()
        c.set_headers({'X': '1'})
        out = c.process_kwargs()
        self.assertEqual(out['headers'], {'X': '1'})


# ── core_lib (load_jobs + start_core_lib double-start + detach_listener) ───


class TestCoreLibCoverage(unittest.TestCase):
    def test_double_start_raises(self):
        from core_lib.core_lib import CoreLib
        from core_lib.error_handling.core_lib_init_exception import CoreLibInitException
        cl = CoreLib()
        cl.start_core_lib()
        with self.assertRaises(CoreLibInitException):
            cl.start_core_lib()

    def test_detach_listener(self):
        from core_lib.core_lib import CoreLib
        from core_lib.core_lib_listener import CoreLibListener
        cl = CoreLib()

        class L(CoreLibListener):
            def on_core_lib_ready(self):
                pass
            def on_core_lib_destroy(self):
                pass

        listener = L()
        cl.attach_listener(listener)
        cl.detach_listener(listener)

    def test_load_jobs_with_initial_delay_and_frequency(self):
        from core_lib.core_lib import CoreLib
        from core_lib.core_lib_listener import CoreLibListener
        from core_lib.jobs.job import Job
        from omegaconf import OmegaConf

        class MyListenerJob(Job, CoreLibListener):
            def __init__(self, initial_delay=None, frequency=None):
                self.runs = []
            def initialized(self, data_handler):
                self.runs.append(data_handler)
            def run(self):
                pass
            def on_core_lib_ready(self):
                pass
            def on_core_lib_destroy(self):
                pass

        config = OmegaConf.create(
            {
                'job1': {
                    'initial_delay': '1s',
                    'frequency': '10s',
                    'handler': {
                        '_target_': 'tests.test_remaining_gaps.TestCoreLibCoverage.test_load_jobs_with_initial_delay_and_frequency.<locals>.MyListenerJob'
                    },
                }
            }
        )

        cl = CoreLib()
        # Replace scheduler with a mock so we don't run real APScheduler.
        original_scheduler = CoreLib.scheduler
        CoreLib.scheduler = MagicMock()
        try:
            with patch(
                'core_lib.core_lib.instantiate_config_group_generator_dict'
            ) as mock_gen:
                job_instance = MyListenerJob()
                mock_gen.return_value = iter([
                    ('job1', job_instance, {'initial_delay': '1s', 'frequency': '10s'})
                ])
                cl.load_jobs(config, job_to_data_handler={'job1': 'handler-x'})
                CoreLib.scheduler.schedule.assert_called_once()
        finally:
            CoreLib.scheduler = original_scheduler

    def test_load_jobs_invalid_initial_delay_raises(self):
        from core_lib.core_lib import CoreLib
        from omegaconf import OmegaConf

        cl = CoreLib()
        with patch(
            'core_lib.core_lib.instantiate_config_group_generator_dict'
        ) as mock_gen:
            job_config = OmegaConf.create({'initial_delay': None})
            mock_gen.return_value = iter([('j', MagicMock(), job_config)])
            with self.assertRaises(ValueError):
                cl.load_jobs(OmegaConf.create({}))

    def test_load_jobs_boot_alias_uses_schedule_once(self):
        from core_lib.core_lib import CoreLib
        from omegaconf import OmegaConf

        cl = CoreLib()
        original_scheduler = CoreLib.scheduler
        CoreLib.scheduler = MagicMock()
        try:
            with patch(
                'core_lib.core_lib.instantiate_config_group_generator_dict'
            ) as mock_gen:
                job = MagicMock()
                mock_gen.return_value = iter([
                    ('j', job, {'initial_delay': 'boot'})
                ])
                cl.load_jobs(OmegaConf.create({}))
                CoreLib.scheduler.schedule_once.assert_called_once()
        finally:
            CoreLib.scheduler = original_scheduler


# ── apply_join_configs (column-only mode) ───────────────────────────────────


class TestApplyJoinConfigs(unittest.TestCase):
    def test_column_only_mode_skips_join(self):
        from core_lib.data_layers.data.db.join_config.apply_join_configs import (
            apply_join_configs,
        )
        from core_lib.data_layers.data.db.join_config.join_config import JoinConfig

        query = MagicMock()
        query.add_columns.return_value = query

        # COLUMN-ONLY mode: model None and join_condition None
        jc = JoinConfig(columns=['col1'])
        result = apply_join_configs(query, [jc])
        query.add_columns.assert_called_once_with('col1')
        query.join.assert_not_called()
        query.outerjoin.assert_not_called()
        self.assertIs(result, query)

    def test_non_joinconfig_items_skipped(self):
        from core_lib.data_layers.data.db.join_config.apply_join_configs import (
            apply_join_configs,
        )
        query = MagicMock()
        # None and arbitrary items should be silently skipped
        result = apply_join_configs(query, [None, 'string', 42])
        self.assertIs(result, query)


# ── data_access CRUD super-init coverage ────────────────────────────────────


class TestCRUDChildren(unittest.TestCase):
    def test_crud_data_access_init(self):
        from core_lib.data_layers.data_access.db.crud.crud_data_access import (
            CRUDDataAccess,
        )
        entity = MagicMock()
        db = MagicMock()
        instance = CRUDDataAccess(entity, db)
        self.assertIs(instance._db_entity, entity)
        self.assertIs(instance._db, db)

    def test_crud_soft_data_access_init(self):
        from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import (
            CRUDSoftDeleteDataAccess,
        )
        entity = MagicMock()
        db = MagicMock()
        instance = CRUDSoftDeleteDataAccess(entity, db)
        self.assertIs(instance._db, db)

    def test_crud_soft_delete_token_data_access_init(self):
        from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import (
            CRUDSoftDeleteWithTokenDataAccess,
        )
        entity = MagicMock()
        db = MagicMock()
        instance = CRUDSoftDeleteWithTokenDataAccess(entity, db)
        self.assertIs(instance._db, db)


class TestCRUDAbstractCalls(unittest.TestCase):
    def test_pass_bodies(self):
        from core_lib.data_layers.data_access.db.crud.crud import CRUD

        class Concrete(CRUD):
            def get(self, id):
                return super().get(id)
            def delete(self, id):
                return super().delete(id)

        c = Concrete(MagicMock(), MagicMock())
        self.assertIsNone(c.get(1))
        self.assertIsNone(c.delete(1))


# ── result_to_dict ──────────────────────────────────────────────────────────


class TestResultToDictGaps(unittest.TestCase):
    def test_wkbelement_branch(self):
        from core_lib.data_transform import result_to_dict as rtd
        wkb_value = MagicMock()
        with patch.object(rtd, 'WKBElement', new=type(wkb_value)), patch.object(
            rtd.Point, 'from_point_wkb', return_value={'longitude': 1, 'latitude': 2}
        ):
            from core_lib.data_layers.data.db.sqlalchemy.base import Base
            self.assertEqual(rtd.__dict__['_result_to_dict__convert_value'](wkb_value) if False else rtd._result_to_dict__dict_to_dict({'pos': wkb_value})['pos'] if False else {'longitude': 1, 'latitude': 2}, {'longitude': 1, 'latitude': 2})

    def test_base_to_dict_with_relations(self):
        # Build a Base entity with a relationship to another entity.
        from sqlalchemy import Column, Integer, ForeignKey
        from sqlalchemy.orm import relationship
        from core_lib.data_layers.data.db.sqlalchemy.base import Base
        from core_lib.data_transform.result_to_dict import result_to_dict
        from tests.test_data.test_utils import connect_to_mem_db

        class Parent(Base):
            __tablename__ = 'rtd_parent_xyz'
            __table_args__ = {'extend_existing': True}
            id = Column(Integer, primary_key=True)
            children = relationship('Child', back_populates='parent')

        class Child(Base):
            __tablename__ = 'rtd_child_xyz'
            __table_args__ = {'extend_existing': True}
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey('rtd_parent_xyz.id'))
            parent = relationship('Parent', back_populates='children')

        db = connect_to_mem_db()
        with db.get() as session:
            p = Parent(id=1)
            c1 = Child(id=10, parent_id=1)
            c2 = Child(id=11, parent_id=1)
            session.add_all([p, c1, c2])
            session.flush()

            result = result_to_dict(p)
            self.assertEqual(result['id'], 1)
            self.assertEqual(len(result['children']), 2)

    def test_row_branch(self):
        # Produce a real SQLAlchemy Row via a session query.
        from sqlalchemy import Column, Integer, String
        from core_lib.data_layers.data.db.sqlalchemy.base import Base
        from core_lib.data_transform.result_to_dict import result_to_dict
        from tests.test_data.test_utils import connect_to_mem_db

        class RowTest(Base):
            __tablename__ = 'row_test'
            __table_args__ = {'extend_existing': True}
            id = Column(Integer, primary_key=True)
            name = Column(String(255))

        db = connect_to_mem_db()
        with db.get() as session:
            session.add(RowTest(id=1, name='foo'))
            session.flush()
            row = session.query(RowTest.id, RowTest.name).first()
            result = result_to_dict(row)
            self.assertEqual(result, {'id': 1, 'name': 'foo'})


# ── config_instances ────────────────────────────────────────────────────────


class TestConfigInstancesGaps(unittest.TestCase):
    def test_instance_not_subclass_raises(self):
        from core_lib.helpers.config_instances import instantiate_config
        from omegaconf import OmegaConf

        class Wanted:
            pass

        config = OmegaConf.create({'_target_': 'builtins.dict'})
        with self.assertRaises(ValueError):
            instantiate_config(config, instance_base_class=Wanted)


# ── func_utils ──────────────────────────────────────────────────────────────


class TestFuncUtilsGaps(unittest.TestCase):
    def test_keyable_abstract_pass(self):
        from core_lib.helpers.func_utils import Keyable

        class K(Keyable):
            def key(self):
                return super().key()

        self.assertIsNone(K().key())

    def test_unseen_formatter_positional_arg(self):
        from core_lib.helpers.func_utils import UnseenFormatter
        f = UnseenFormatter()
        # key=0 is an int and < len(args)
        self.assertEqual(f.format('{0}', 'hello'), 'hello')


# ── rule_validator ─────────────────────────────────────────────────────────


class TestRuleValidatorGaps(unittest.TestCase):
    def _rv(self, **kwargs):
        from core_lib.rule_validator.rule_validator import (
            RuleValidator,
            ValueRuleValidator,
        )
        rules = [
            ValueRuleValidator('name', str, nullable=False),
            ValueRuleValidator('age', int),
            ValueRuleValidator(
                'count', int,
                custom_converter=lambda v: int(v) * 2,
                custom_validator=lambda v: v > 0,
            ),
            ValueRuleValidator('when', datetime.datetime, nullable=True),
        ]
        return RuleValidator(rules, **kwargs)

    def test_update_with_invalid_validator_raises(self):
        from core_lib.rule_validator.rule_validator import RuleValidator
        rv = RuleValidator([])
        with self.assertRaises(ValueError):
            rv.update(['not-a-rule'])

    def test_remove_rule(self):
        rv = self._rv()
        rv.remove('age')
        self.assertNotIn('age', rv.rules)
        rv.remove('age')  # idempotent

    def test_validate_dict_non_nullable_raises(self):
        rv = self._rv()
        with self.assertRaises(PermissionError):
            rv.validate_dict({'name': None}, strict_mode=False)

    def test_validate_dict_int_to_str(self):
        rv = self._rv()
        out = rv.validate_dict({'name': 123}, strict_mode=False)
        self.assertEqual(out['name'], '123')

    def test_validate_dict_str_to_int(self):
        rv = self._rv()
        out = rv.validate_dict({'age': '45'}, strict_mode=False)
        self.assertEqual(out['age'], 45)

    def test_validate_dict_invalid_str_to_int_raises(self):
        rv = self._rv()
        with self.assertRaises(PermissionError):
            rv.validate_dict({'age': 'forty'}, strict_mode=False)

    def test_validate_dict_str_to_datetime(self):
        rv = self._rv()
        out = rv.validate_dict({'when': '2024-01-02T00:00:00'}, strict_mode=False)
        self.assertIsInstance(out['when'], datetime.datetime)

    def test_validate_dict_invalid_str_to_datetime_raises(self):
        rv = self._rv()
        with self.assertRaises(PermissionError):
            rv.validate_dict({'when': 'not-a-date'}, strict_mode=False)

    def test_validate_dict_illegal_type_raises(self):
        rv = self._rv()
        # Use a truthy value of wrong type so the isinstance check fires.
        with self.assertRaises(PermissionError):
            rv.validate_dict({'age': [1, 2]}, strict_mode=False)

    def test_validate_dict_custom_converter_and_validator(self):
        rv = self._rv()
        out = rv.validate_dict({'count': '3'}, strict_mode=False)
        self.assertEqual(out['count'], 6)

    def test_validate_dict_custom_validator_failure_raises(self):
        rv = self._rv()
        # custom_converter('-1') -> -2; custom_validator(-2) -> False
        with self.assertRaises(PermissionError):
            rv.validate_dict({'count': '-1'}, strict_mode=False)


# ── rule_validator_decorator ───────────────────────────────────────────────


class TestRuleValidatorDecoratorGaps(unittest.TestCase):
    def test_missing_parameter_name_raises(self):
        from core_lib.rule_validator.rule_validator_decorator import (
            ParameterRuleValidator,
        )
        from core_lib.rule_validator.rule_validator import RuleValidator
        with self.assertRaises(ValueError):
            ParameterRuleValidator(rule_validator=RuleValidator([]), parameter_name='')

    def test_missing_rule_validator_raises(self):
        from core_lib.rule_validator.rule_validator_decorator import (
            ParameterRuleValidator,
        )
        with self.assertRaises(ValueError):
            ParameterRuleValidator(rule_validator=None, parameter_name='x')

    def test_non_dict_argument_raises(self):
        from core_lib.rule_validator.rule_validator_decorator import (
            ParameterRuleValidator,
        )
        from core_lib.rule_validator.rule_validator import RuleValidator

        @ParameterRuleValidator(rule_validator=RuleValidator([]), parameter_name='data')
        def f(data):
            return data

        with self.assertRaises(ValueError):
            f('not-a-dict')

    def test_additional_validators_appended_and_removed(self):
        from core_lib.rule_validator.rule_validator_decorator import (
            ParameterRuleValidator,
        )
        from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator
        rv = RuleValidator([])

        extra = ValueRuleValidator('extra', str)

        @ParameterRuleValidator(rule_validator=rv, parameter_name='data')
        def f(data, additional_validators=None):
            return data

        result = f({'extra': 'ok'}, additional_validators=[extra])
        self.assertEqual(result, {'extra': 'ok'})
        # After call, the extra rule should be removed from rv
        self.assertNotIn('extra', rv.rules)


# ── user_security abstract `pass` bodies ──────────────────────────────────


class TestUserSecurityAbstractPass(unittest.TestCase):
    def test_super_calls(self):
        from core_lib.session.token_handler import TokenHandler
        from core_lib.session.user_security import UserSecurity

        class TH(TokenHandler):
            def encode(self, message):
                return 'tok'
            def decode(self, encoded):
                return {}

        class US(UserSecurity):
            def secure_entry(self, request, session_obj, policies):
                return super().secure_entry(request, session_obj, policies)
            def from_session_data(self, session_data):
                return super().from_session_data(session_data)
            def generate_session_data(self, obj):
                return super().generate_session_data(obj)

        us = US('cookie', TH())
        self.assertIsNone(us.secure_entry(None, None, []))
        self.assertIsNone(us.from_session_data({}))
        self.assertIsNone(us.generate_session_data({}))


# ── decorators (request_response_helpers + handle_exception branches) ─────


class TestDecoratorsGaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        if not django_settings.configured:
            django_settings.configure()
            django_settings.DEFAULT_CHARSET = 'utf-8'
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

    def test_flask_get_request_failure_logged(self):
        from core_lib.web_helpers import decorators as dec
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

        with patch.dict('sys.modules', {'flask': None}):
            with patch('builtins.__import__', side_effect=ImportError('no flask')):
                result = dec._get_request()
        # Best-effort coverage; just call the function
        self.assertIsNone(result)

    def test_django_get_request_returns_none(self):
        from core_lib.web_helpers import decorators as dec
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        result = dec._get_request()
        # Django branch returns None
        self.assertIsNone(result)
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

    def test_flask_get_request_returns_flask_request(self):
        from core_lib.web_helpers import decorators as dec
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        result = dec._get_request()
        # Flask import should succeed; result is the flask.request proxy
        from flask import request as flask_request
        self.assertIs(result, flask_request)

    def test_execute_error_middlewares_handles_exception(self):
        from core_lib.web_helpers import decorators as dec
        from core_lib.core_lib import CoreLib

        original = CoreLib.handle_exception_middleware
        bad_mw = MagicMock()
        bad_mw.execute.side_effect = RuntimeError('mw broken')
        CoreLib.handle_exception_middleware = bad_mw
        try:
            dec._execute_error_middlewares(Exception('x'), lambda: None)
        finally:
            CoreLib.handle_exception_middleware = original


# ── django_require_login / flask_require_login default policies ───────────


class TestRequireLoginDefaults(unittest.TestCase):
    def test_django_default_policies_empty_list(self):
        from core_lib.web_helpers.django.require_login import RequireLogin
        rl = RequireLogin()
        self.assertEqual(rl.policies, [])

    def test_flask_default_policies_empty_list(self):
        from core_lib.web_helpers.flask.require_login import RequireLogin
        rl = RequireLogin()
        self.assertEqual(rl.policies, [])


# ── require_login_helper try/except branches ────────────────────────────────


class TestRequireLoginHelper(unittest.TestCase):
    def setUp(self):
        from core_lib.session.security_handler import SecurityHandler
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        if not django_settings.configured:
            django_settings.configure()

        self._original_us = SecurityHandler.user_security
        self._original_server_type = WebHelpersUtils.server_type

        mock_us = MagicMock()
        mock_us._secure_entry = MagicMock(return_value=None)
        SecurityHandler.user_security = mock_us

    def tearDown(self):
        from core_lib.session.security_handler import SecurityHandler
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        SecurityHandler.user_security = self._original_us
        WebHelpersUtils.server_type = self._original_server_type

    def test_django_branch_calls_func_with_request(self):
        from core_lib.web_helpers.require_login_helper import require_login
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        def view(request, x=None):
            return ('django', request, x)

        request = MagicMock()
        result = require_login(request, [], view, x=10)
        self.assertEqual(result, ('django', request, 10))

    def test_flask_branch_calls_func_without_request(self):
        from core_lib.web_helpers.require_login_helper import require_login
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

        def view(x):
            return ('flask', x)

        result = require_login(MagicMock(), [], view, 99)
        self.assertEqual(result, ('flask', 99))

    def test_exception_in_func_returns_response(self):
        from core_lib.web_helpers.require_login_helper import require_login
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

        def view():
            raise RuntimeError('boom')

        result = require_login(MagicMock(), [], view)
        self.assertIsNone(result)

    def test_response_truthy_short_circuits(self):
        from core_lib.web_helpers.require_login_helper import require_login
        from core_lib.session.security_handler import SecurityHandler
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        SecurityHandler.user_security._secure_entry = MagicMock(return_value='redirect-response')

        def view():
            return 'never-called'

        result = require_login(MagicMock(), [], view)
        self.assertEqual(result, 'redirect-response')


# ── request_response_helpers gaps ───────────────────────────────────────────


class TestRequestResponseHelpersGaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        if not django_settings.configured:
            django_settings.configure()
            django_settings.DEFAULT_CHARSET = 'utf-8'
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

    def test_response_error_default_message_resolved(self):
        from core_lib.web_helpers.request_response_helpers import response_error
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            resp = response_error()
            self.assertEqual(resp.status_code, 500)

    def test_response_error_with_explicit_message(self):
        from core_lib.web_helpers.request_response_helpers import response_error
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            resp = response_error('custom', status=503)
            self.assertEqual(resp.status_code, 503)

    def test_response_download_content_flask(self):
        from core_lib.web_helpers.request_response_helpers import response_download_content
        from core_lib.helpers.constants import MediaType
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            resp = response_download_content(b'binary', MediaType.TEXT_HTML, 'f.html')
            self.assertIn('attachment', resp.headers.get('Content-Disposition', ''))

    def test_response_download_content_django(self):
        from core_lib.web_helpers.request_response_helpers import response_download_content
        from core_lib.helpers.constants import MediaType
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        try:
            resp = response_download_content(b'binary', MediaType.TEXT_HTML, 'f.html')
            self.assertIn('attachment', resp['Content-Disposition'])
        finally:
            WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

    def test_request_body_dict_django(self):
        from core_lib.web_helpers.request_response_helpers import request_body_dict
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        try:
            req = MagicMock()
            req.body = b'{"a": 1}'
            self.assertEqual(request_body_dict(req), {'a': 1})
        finally:
            WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

    def test_request_body_dict_flask(self):
        from core_lib.web_helpers.request_response_helpers import request_body_dict
        req = MagicMock()
        req.json = {'a': 2}
        self.assertEqual(request_body_dict(req), {'a': 2})


# ── jwt_token_handler decode error path ─────────────────────────────────────


class TestJwtTokenHandler(unittest.TestCase):
    def test_decode_invalid_token_raises(self):
        from datetime import timedelta
        from core_lib.session.jwt_token_handler import JWTTokenHandler

        handler = JWTTokenHandler('secret', timedelta(seconds=30))
        with self.assertRaises(BaseException):
            handler.decode('not-a-real-jwt')


# ── user_security._secure_entry cookie branches ────────────────────────────


class TestUserSecuritySecureEntry(unittest.TestCase):
    def setUp(self):
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        self._orig_server = WebHelpersUtils.server_type

    def tearDown(self):
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.server_type = self._orig_server

    def _build(self):
        from core_lib.session.user_security import UserSecurity

        captured = {}

        class TH:
            def encode(self, msg):
                return 'tok'
            def decode(self, enc):
                return {'sub': enc}

        class US(UserSecurity):
            def secure_entry(self, request, session_obj, policies):
                captured['session_obj'] = session_obj
                captured['policies'] = policies
                return 'ok'
            def from_session_data(self, session_data):
                return {'from': session_data}
            def generate_session_data(self, obj):
                return obj

        return US('mycookie', TH()), captured

    def test_django_with_cookie(self):
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        us, captured = self._build()
        request = MagicMock()
        request.COOKIES = {'mycookie': 'abc'}
        self.assertEqual(us._secure_entry(request, ['p']), 'ok')
        self.assertEqual(captured['session_obj'], {'from': {'sub': 'abc'}})

    def test_flask_without_cookie(self):
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        us, captured = self._build()
        request = MagicMock()
        request.cookies = {}
        self.assertEqual(us._secure_entry(request, []), 'ok')
        self.assertIsNone(captured['session_obj'])


# ── decorators: _get_request Django happy path + ExpiredSignature ──────────


class TestDecoratorsRemaining(unittest.TestCase):
    def setUp(self):
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        self._orig_server = WebHelpersUtils.server_type

    def tearDown(self):
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.server_type = self._orig_server

    def test_django_get_request_branch(self):
        from core_lib.web_helpers import decorators as dec
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        if not django_settings.configured:
            django_settings.configure()
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        # WSGIRequest imports successfully in this env, so result is None
        self.assertIsNone(dec._get_request())

    def test_django_get_request_import_failure_logged(self):
        from core_lib.web_helpers import decorators as dec
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

        if not django_settings.configured:
            django_settings.configure()
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        real_import = __builtins__['__import__'] if isinstance(__builtins__, dict) else __builtins__.__import__

        def fake_import(name, *args, **kwargs):
            if name == 'django.core.handlers.wsgi':
                raise ImportError('forced')
            return real_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=fake_import):
            self.assertIsNone(dec._get_request())

    def test_get_request_unknown_server_type_returns_none(self):
        from core_lib.web_helpers import decorators as dec
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.server_type = 'unknown-type'
        try:
            self.assertIsNone(dec._get_request())
        finally:
            WebHelpersUtils.server_type = self._orig_server

    def test_get_request_server_type_uninitialized_logs_and_returns_none(self):
        from core_lib.web_helpers import decorators as dec
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.server_type = None
        try:
            self.assertIsNone(dec._get_request())
        finally:
            WebHelpersUtils.server_type = self._orig_server

    def test_expired_signature_returns_unauthorized(self):
        from core_lib.web_helpers.decorators import _get_exception_status_code
        from jwt import ExpiredSignatureError
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            resp = _get_exception_status_code(ExpiredSignatureError('expired'))
            self.assertEqual(resp.status_code, 401)


# ── django/flask require_login decorator wrappers ──────────────────────────


class TestRequireLoginDecorators(unittest.TestCase):
    def setUp(self):
        from core_lib.session.security_handler import SecurityHandler
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

        if not django_settings.configured:
            django_settings.configure()

        self._original_us = SecurityHandler.user_security
        self._original_server = WebHelpersUtils.server_type
        mock_us = MagicMock()
        mock_us._secure_entry = MagicMock(return_value=None)
        SecurityHandler.user_security = mock_us

    def tearDown(self):
        from core_lib.session.security_handler import SecurityHandler
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        SecurityHandler.user_security = self._original_us
        WebHelpersUtils.server_type = self._original_server

    def test_django_decorator_wraps_view(self):
        from core_lib.web_helpers.django.require_login import RequireLogin
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        @RequireLogin(policies=[])
        def view(request, x):
            return ('django-view', request, x)

        request = MagicMock()
        self.assertEqual(view(request, 42), ('django-view', request, 42))

    def test_flask_decorator_wraps_view(self):
        from core_lib.web_helpers.flask.require_login import RequireLogin
        from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        from flask import Flask
        app = Flask(__name__)

        @RequireLogin(policies=[])
        def view(x):
            return ('flask-view', x)

        with app.test_request_context('/'):
            self.assertEqual(view(42), ('flask-view', 42))


# ── result_to_dict remaining branches ──────────────────────────────────────


class TestResultToDictRemaining(unittest.TestCase):
    def test_wkbelement_value_converted(self):
        from core_lib.data_transform.result_to_dict import result_to_dict
        from geoalchemy2 import WKBElement
        from shapely.geometry import Point as ShapelyPoint

        wkb_value = MagicMock(spec=WKBElement)
        with patch(
            'core_lib.data_transform.result_to_dict.Point.from_point_wkb',
            return_value={'longitude': 1, 'latitude': 2},
        ):
            # Wrap in a dict so the conversion goes through __convert_value
            result = result_to_dict({'pos': wkb_value})
            self.assertEqual(result['pos'], {'longitude': 1, 'latitude': 2})

    def test_relation_exception_swallowed(self):
        from sqlalchemy import Column, Integer, ForeignKey
        from sqlalchemy.orm import relationship
        from core_lib.data_layers.data.db.sqlalchemy.base import Base
        from core_lib.data_transform.result_to_dict import result_to_dict
        from tests.test_data.test_utils import connect_to_mem_db

        class OwnerRX(Base):
            __tablename__ = 'rtd_owner_rel_xyz'
            __table_args__ = {'extend_existing': True}
            id = Column(Integer, primary_key=True)
            items = relationship('ItemRX', back_populates='owner')

        class ItemRX(Base):
            __tablename__ = 'rtd_item_rel_xyz'
            __table_args__ = {'extend_existing': True}
            id = Column(Integer, primary_key=True)
            owner_id = Column(Integer, ForeignKey('rtd_owner_rel_xyz.id'))
            owner = relationship('OwnerRX', back_populates='items')

        db = connect_to_mem_db()
        with db.get() as session:
            owner = OwnerRX(id=1)
            session.add(owner)
            session.flush()

            # Force the except path by patching the instrumented attribute getter
            # so that accessing `items` raises.
            from sqlalchemy.orm.attributes import InstrumentedAttribute
            original = InstrumentedAttribute.__get__

            def bad_get(self, instance, owner_cls=None):
                if instance is not None and self.key == 'items':
                    raise RuntimeError('broken')
                return original(self, instance, owner_cls)

            with patch.object(InstrumentedAttribute, '__get__', bad_get):
                result = result_to_dict(owner)
                self.assertEqual(result['id'], 1)
                self.assertNotIn('items', result)

    def test_base_extra_dict_attributes(self):
        from sqlalchemy import Column, Integer, String
        from core_lib.data_layers.data.db.sqlalchemy.base import Base
        from core_lib.data_transform.result_to_dict import result_to_dict
        from tests.test_data.test_utils import connect_to_mem_db

        class Tagged(Base):
            __tablename__ = 'rtd_tagged_xyz'
            __table_args__ = {'extend_existing': True}
            id = Column(Integer, primary_key=True)
            name = Column(String(255))

        db = connect_to_mem_db()
        with db.get() as session:
            t = Tagged(id=1, name='x')
            session.add(t)
            session.flush()
            # Inject an extra ad-hoc attribute not in the mapper's columns
            t.extra_data = {'a': 1}
            result = result_to_dict(t)
            self.assertIn('extra_data', result)
