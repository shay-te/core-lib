"""A plain `pip install core-lib` (no extras) imports and runs the core: CoreLib, CRUD on SQLite, decorators, jobs, CLI."""
import os
import subprocess
import sys
import textwrap
import unittest

from tests.test_setup_extras import OPTIONAL_MODULES

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Every module only an extra installs: the backends, and the [test] extra's tools. Setting
# sys.modules[name] = None makes `import name` raise ImportError, as if it were not installed.
OPTIONAL_PACKAGES = OPTIONAL_MODULES + ['mongomock', 'fakeredis', 'moto', 'boto3', 'freezegun', 'flask_wtf', 'pandas']

# The only modules a core install cannot import, because what each one does needs the package it is missing. Anything
# else imports without an extra: a module that needs a backend for one function imports it in that function.
MODULES_THAT_NEED_AN_EXTRA = {
    'core_lib.cache.cache_handler_memcached',
    'core_lib.cache.cache_handler_redis',
    'core_lib.connection.elasticsearch_connection',
    'core_lib.connection.elasticsearch_connection_factory',
    'core_lib.connection.mongodb_connection',
    'core_lib.connection.mongodb_connection_factory',
    'core_lib.connection.neo4j_connection',
    'core_lib.connection.neo4j_connection_factory',
    'core_lib.connection.solr_connection',
    'core_lib.connection.solr_connection_factory',
    'core_lib.helpers.parse_utils',                       # pandas; its page says to install it
    'core_lib.session.jwt_token_handler',
    'core_lib.web_helpers.decorators',                    # the rest need Flask or Django, whose extras bring PyJWT
    'core_lib.web_helpers.django.require_login',
    'core_lib.web_helpers.django.user_auth_middleware',
    'core_lib.web_helpers.flask.require_login',
    'core_lib.web_helpers.flask.user_auth_middleware',
    'core_lib.web_helpers.require_login_helper',
}

IMPORT_EVERY_MODULE = textwrap.dedent('''
    import importlib, pkgutil, sys, warnings
    warnings.simplefilter('ignore')                                 # the deprecated aliases warn on import
    for name in OPTIONAL_PACKAGES:
        sys.modules[name] = None

    import core_lib
    for module in pkgutil.walk_packages(core_lib.__path__, 'core_lib.'):
        try:
            importlib.import_module(module.name)
            print('imported', module.name)
        except ImportError:
            print('needs an extra', module.name)
''')

CORE_SCRIPT = textwrap.dedent('''
    import enum, sys
    from datetime import datetime
    for name in OPTIONAL_PACKAGES:
        sys.modules[name] = None

    from omegaconf import OmegaConf
    from sqlalchemy import Column, DateTime, INTEGER, VARCHAR

    import core_lib.core_lib_main                                   # the `core_lib` CLI
    from core_lib.alembic.alembic import Alembic
    from core_lib.cache.cache_decorator import Cache
    from core_lib.cache.cache_handler_ram import CacheHandlerRam
    from core_lib.client.client_base import ClientBase
    from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
    from core_lib.core_lib import CoreLib
    from core_lib.data_layers.data.db.sqlalchemy.base import Base
    from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum
    from core_lib.data_layers.data_access.db.crud.crud_soft_delete_data_access import CRUDSoftDeleteDataAccess
    from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
    from core_lib.data_layers.service.service import Service
    from core_lib.data_transform.result_to_dict import ResultToDict
    from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
    from core_lib.helpers.config_instances import instantiate_config
    from core_lib.helpers.test import load_core_lib_config
    from core_lib.jobs.job_scheduler import JobScheduler
    from core_lib.middleware.middleware_chain import MiddlewareChain
    from core_lib.observer.observer import Observer
    from core_lib.observer.observer_decorator import Observe
    from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
    from core_lib.rule_validator.helpers import convert_datetime, convert_location, validate_location
    from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator

    assert convert_datetime(datetime(2024, 1, 1)) == datetime(2024, 1, 1)
    assert validate_location(convert_location({'latitude': 32.0853, 'longitude': 34.7818}))
    assert Point.from_point_str(Point.to_point_str(34.7818, 32.0853)) == {'latitude': 32.0853, 'longitude': 34.7818}
    try:
        Point.from_point_wkb(None)                                  # the one path that does need the [geo] extra
    except ImportError:
        pass
    else:
        raise AssertionError('from_point_wkb needs geoalchemy2')

    class Kind(enum.Enum):
        ALPHA = 1

    class Widget(Base, SoftDeleteMixin):
        __tablename__ = 'core_install_widget'
        id = Column(INTEGER, primary_key=True)
        name = Column(VARCHAR(length=50), nullable=False)
        kind = Column(IntEnum(Kind), nullable=False)
        made_at = Column(DateTime)

    class WidgetDataAccess(CRUDSoftDeleteDataAccess):
        def __init__(self, db):
            super().__init__(Widget, db, RuleValidator([ValueRuleValidator(Widget.name.key, str)]))

    class WidgetService(Service):
        def __init__(self, widget_da):
            self._widget_da = widget_da

        @ResultToDict()
        @DuplicateErrorHandler()
        def create(self, data):
            return self._widget_da.create(data)

        @Cache('acme_widget_{widget_id}', handler_name='acme')
        @ResultToDict()
        def get(self, widget_id):
            return self._widget_da.get(widget_id)

    class AcmeCoreLib(CoreLib):
        def __init__(self):
            super().__init__()
            if not CoreLib.cache_registry.get('acme'):
                CoreLib.cache_registry.register('acme', CacheHandlerRam())
            if not CoreLib.observer_registry.get('acme'):
                CoreLib.observer_registry.register('acme', Observer())
            db = SqlAlchemyConnectionFactory(OmegaConf.create({'create_db': True, 'url': {'protocol': 'sqlite'}}))
            self.widget = WidgetService(WidgetDataAccess(db))

    acme = AcmeCoreLib()
    acme.start_core_lib()
    created = acme.widget.create({Widget.name.key: 'widget', Widget.kind.key: Kind.ALPHA,
                                  Widget.made_at.key: datetime(2024, 1, 1)})
    fetched = acme.widget.get(created[Widget.id.key])
    print(fetched[Widget.name.key], fetched[Widget.kind.key], type(fetched[Widget.made_at.key]).__name__)
''')


class TestCoreInstall(unittest.TestCase):

    def test_core_runs_without_any_extra(self):
        script = f'OPTIONAL_PACKAGES = {OPTIONAL_PACKAGES!r}\n' + CORE_SCRIPT
        environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', script], cwd=REPO_ROOT, env=environment, capture_output=True, text=True, timeout=120
        )

        self.assertEqual(0, result.returncode, result.stderr[-3000:])
        self.assertEqual('widget 1 float', result.stdout.strip().splitlines()[-1])

    def test_only_modules_that_need_a_backend_stop_importing_without_an_extra(self):
        script = f'OPTIONAL_PACKAGES = {OPTIONAL_PACKAGES!r}\n' + IMPORT_EVERY_MODULE
        environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', script], cwd=REPO_ROOT, env=environment, capture_output=True, text=True, timeout=120
        )

        self.assertEqual(0, result.returncode, result.stderr[-3000:])
        lines = result.stdout.splitlines()
        needs_an_extra = {line.split()[-1] for line in lines if line.startswith('needs an extra ')}
        self.assertEqual(MODULES_THAT_NEED_AN_EXTRA, needs_an_extra)
        self.assertIn('imported core_lib.rule_validator.helpers', lines)   # so an empty walk cannot pass
