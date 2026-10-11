"""A plain `pip install core-lib` (no extras) imports and runs the core: CoreLib, CRUD on SQLite, decorators, jobs, CLI."""
import os
import subprocess
import sys
import textwrap
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Every package that is only installed by an extra. Setting sys.modules[name] = None makes
# `import name` raise ImportError, as if the package were not installed.
OPTIONAL_PACKAGES = [
    'flask', 'flask_cors', 'flask_wtf', 'werkzeug', 'django', 'jwt', 'cryptography',
    'psycopg2', 'pymysql', 'pymongo', 'mongomock', 'pysolr', 'neo4j', 'redis', 'memcache',
    'elasticsearch', 'geoalchemy2', 'shapely', 'numpy', 'pandas', 'boto3', 'moto', 'freezegun',
]

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
    from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
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
    from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator

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
