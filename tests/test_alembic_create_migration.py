"""Alembic against a real SQLite file: create_migration refuses an empty name and writes nothing, numbers the
revisions it creates and records the latest in the version file; upgrade/downgrade walk the revisions; history lists
them; and the constructor refuses a migrations folder or version file name it cannot use."""
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

from omegaconf import OmegaConf
from sqlalchemy import Column, Integer, VARCHAR, create_engine, inspect, text
from sqlalchemy.orm import declarative_base

from core_lib.alembic.alembic import Alembic

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_MIGRATIONS = os.path.join(
    REPO_ROOT, 'core_lib_generator', 'template_core_lib', 'template_core_lib', 'data_layers', 'data', 'db', 'migrations'
)
VERSION_FILE_NAME = '.migration_ver'
VERSION_TABLE = 'acme_alembic_version'

# A base of its own, so these tables never join core-lib's shared Base.metadata.
LocalBase = declarative_base()


class Widget(LocalBase):
    __tablename__ = 'acme_alembic_widget'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(length=50), nullable=False)


class Gadget(LocalBase):
    __tablename__ = 'acme_alembic_gadget'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(length=50), nullable=False)


# What a developer writes into a revision create_migration made, in place of its empty upgrade() and downgrade().
MIGRATION_BODY = '''from {module} import {entity}


def upgrade():
    op.create_table(
        {entity}.__tablename__,
        sa.Column({entity}.id.key, sa.Integer, primary_key=True),
        sa.Column({entity}.name.key, sa.VARCHAR(length=50), nullable=False),
    )


def downgrade():
    op.drop_table({entity}.__tablename__)
'''


class TestAlembicCreateMigration(unittest.TestCase):

    def setUp(self):
        self.core_lib_path = tempfile.mkdtemp()
        self.migrations_path = os.path.join(self.core_lib_path, 'migrations')
        os.makedirs(os.path.join(self.migrations_path, 'versions'))
        shutil.copy(os.path.join(TEMPLATE_MIGRATIONS, 'script.py.mako'), self.migrations_path)
        self.db_path = os.path.join(self.core_lib_path, 'acme.db')
        self.alembic = Alembic(self.core_lib_path, OmegaConf.create(self._config()))

    def tearDown(self):
        shutil.rmtree(self.core_lib_path)

    def _config(self, **alembic_overrides) -> dict:
        alembic = {
            'script_location': 'migrations',
            'file_template': '%%(rev)s_%%(slug)s',
            'version_table': VERSION_TABLE,
            'version_file_name': VERSION_FILE_NAME,
            'render_as_batch': False,
            **alembic_overrides,
        }
        # build_url strips a leading '/', so the SQLite file is given relative to the working directory.
        url = {'protocol': 'sqlite', 'file': os.path.relpath(self.db_path)}
        sqlalchemy = {'config': {'log_queries': False, 'url': url}}
        return {'core_lib': {'alembic': alembic, 'data': {'sqlalchemy': sqlalchemy}}}

    def _revision_files(self):
        return sorted(name for name in os.listdir(os.path.join(self.migrations_path, 'versions')) if name.endswith('.py'))

    def _create_revision(self, name: str, entity):
        self.alembic.create_migration(name)
        revision_file = os.path.join(self.migrations_path, 'versions', self._revision_files()[-1])
        with open(revision_file) as file:
            generated = file.read()
        body = MIGRATION_BODY.format(module=__name__, entity=entity.__name__)
        with open(revision_file, 'w') as file:
            file.write(generated[:generated.index('def upgrade():')] + body)

    def _database(self):
        engine = create_engine(f'sqlite:///{self.db_path}')
        try:
            tables = set(inspect(engine).get_table_names())
            revisions = []
            if VERSION_TABLE in tables:
                with engine.connect() as connection:
                    revisions = connection.execute(text(f'SELECT version_num FROM {VERSION_TABLE}')).scalars().all()
            return tables, revisions
        finally:
            engine.dispose()

    def test_empty_name_raises_value_error_and_writes_nothing(self):
        for empty_name in ('', None):
            with self.assertRaisesRegex(ValueError, 'Migration name must be set'):
                self.alembic.create_migration(empty_name)
        self.assertEqual([], self._revision_files())
        self.assertFalse(os.path.exists(os.path.join(self.migrations_path, VERSION_FILE_NAME)))

    def test_create_migration_numbers_revisions_and_records_the_latest(self):
        self.alembic.create_migration('create widget')
        self.alembic.create_migration('add gadget')

        self.assertEqual(['1_create_widget.py', '2_add_gadget.py'], self._revision_files())
        with open(os.path.join(self.migrations_path, VERSION_FILE_NAME)) as version_file:
            self.assertEqual('2', version_file.read())
        with open(os.path.join(self.migrations_path, 'versions', '2_add_gadget.py')) as revision_file:
            self.assertIn("down_revision = '1'", revision_file.read())

    def test_upgrade_and_downgrade_walk_the_revisions(self):
        self._create_revision('create widget', Widget)
        self._create_revision('add gadget', Gadget)

        self.alembic.upgrade()
        self.assertEqual(({Widget.__tablename__, Gadget.__tablename__, VERSION_TABLE}, ['2']), self._database())

        self.alembic.downgrade('-1')
        self.assertEqual(({Widget.__tablename__, VERSION_TABLE}, ['1']), self._database())

        self.alembic.upgrade('+1')
        self.assertEqual(({Widget.__tablename__, Gadget.__tablename__, VERSION_TABLE}, ['2']), self._database())

        self.alembic.downgrade()
        self.assertEqual(({VERSION_TABLE}, []), self._database())

    def test_history_lists_the_revisions_newest_first(self):
        self._create_revision('create widget', Widget)
        self._create_revision('add gadget', Gadget)
        # Alembic prints the history to the process's standard output, so it runs in a process of its own.
        script = textwrap.dedent(f'''
            from omegaconf import OmegaConf
            from core_lib.alembic.alembic import Alembic
            Alembic({self.core_lib_path!r}, OmegaConf.create({self._config()!r})).history()
        ''')

        result = subprocess.run(
            [sys.executable, '-c', script], cwd=os.getcwd(), capture_output=True, text=True, timeout=120,
            env=dict(os.environ, PYTHONPATH=REPO_ROOT, PYTHONDONTWRITEBYTECODE='1'),
        )

        self.assertEqual(0, result.returncode, result.stderr[-3000:])
        self.assertEqual(['1 -> 2 (head), add gadget', '<base> -> 1, create widget'], result.stdout.splitlines())

    def test_constructor_refuses_a_migrations_folder_it_cannot_use(self):
        # Missing, not a folder that exists, or absolute: script_location must be relative to core_lib_path.
        for script_location in ('', 'no_such_migrations', self.migrations_path):
            with self.assertRaises(ValueError) as refused:
                Alembic(self.core_lib_path, OmegaConf.create(self._config(script_location=script_location)))

            self.assertEqual(
                f'config.alembic.script_location does not exist `{script_location}` '
                f'(it must be a folder relative to `{self.core_lib_path}`)',
                str(refused.exception),
            )

    def test_constructor_refuses_a_missing_version_file_name(self):
        with self.assertRaisesRegex(ValueError, 'config.alembic.version_file_name cannot be None'):
            Alembic(self.core_lib_path, OmegaConf.create(self._config(version_file_name=None)))
