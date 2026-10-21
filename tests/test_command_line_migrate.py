"""`core_lib migrate`, run as a real command from a project root against a real SQLite file: `--rev new --name`
numbers revision files, `head` / `base` / `-N` / `N` move the database through them, `--env_file` picks the
environment file that names the database, and a `--rev` value it does not know runs nothing."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

from sqlalchemy import Column, Integer, VARCHAR, create_engine, inspect, text
from sqlalchemy.orm import declarative_base

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_LIB_COMMAND = os.path.join(REPO_ROOT, 'bin', 'core_lib')
TEMPLATE_MIGRATIONS = os.path.join(
    REPO_ROOT, 'core_lib_generator', 'template_core_lib', 'template_core_lib', 'data_layers', 'data', 'db', 'migrations'
)

PROJECT_MODULE = 'acme_core_lib'
MIGRATIONS = os.path.join(PROJECT_MODULE, 'data_layers', 'data', 'db', 'migrations')  # core_lib.yaml's default
VERSION_TABLE = 'acme_alembic_version'
DB_FILE_VARIABLE = 'ACME_DB_FILE'

# The project root, as the Migrations docs describe it: core_lib_config.yaml composes Core-Lib's config with the
# project's own, which names the database through an environment variable.
CORE_LIB_CONFIG_YAML = textwrap.dedent(f'''
    defaults:
      - _self_
      - core_lib
      - acme_migrations

    core_lib_module: {PROJECT_MODULE}

    hydra:
      run:
        dir: .
''')
PROJECT_CONFIG_YAML = textwrap.dedent(f'''
    # @package _global_
    core_lib:
      data:
        sqlalchemy:
          config:
            url:
              file: ${{oc.env:{DB_FILE_VARIABLE}}}
      alembic:
        version_table: {VERSION_TABLE}
''')

# A base of its own, so these tables never join core-lib's shared Base.metadata.
LocalBase = declarative_base()


class Widget(LocalBase):
    __tablename__ = 'acme_cli_widget'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(length=50), nullable=False)


class Gadget(LocalBase):
    __tablename__ = 'acme_cli_gadget'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(length=50), nullable=False)


# What a developer writes into a revision `--rev new` made, in place of its empty upgrade() and downgrade().
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


class TestCommandLineMigrate(unittest.TestCase):

    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        self.migrations = os.path.join(self.project_root, MIGRATIONS)
        os.makedirs(os.path.join(self.migrations, 'versions'))
        shutil.copy(os.path.join(TEMPLATE_MIGRATIONS, 'script.py.mako'), self.migrations)
        self._write('core_lib_config.yaml', CORE_LIB_CONFIG_YAML)
        self._write('acme_migrations.yaml', PROJECT_CONFIG_YAML)
        self._write('.env', f'{DB_FILE_VARIABLE}=acme.db\n')

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def _write(self, name: str, content: str):
        with open(os.path.join(self.project_root, name), 'w') as file:
            file.write(content)

    def _migrate(self, *arguments) -> str:
        environment = dict(os.environ, PYTHONPATH=REPO_ROOT, PYTHONDONTWRITEBYTECODE='1')
        environment.pop(DB_FILE_VARIABLE, None)  # only the env file names the database
        result = subprocess.run(
            [sys.executable, CORE_LIB_COMMAND, 'migrate', *arguments],
            cwd=self.project_root, env=environment, capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(0, result.returncode, result.stderr[-3000:])
        return result.stdout

    def _revision_files(self) -> list:
        versions = os.path.join(self.migrations, 'versions')
        return sorted(name for name in os.listdir(versions) if name.endswith('.py'))

    def _new_revision(self, name: str, entity) -> str:
        stdout = self._migrate('--rev', 'new', '--name', name)
        self.assertIn(f'new revision named `{name}`', stdout)
        revision_file = os.path.join(self.migrations, 'versions', self._revision_files()[-1])
        with open(revision_file) as file:
            generated = file.read()
        body = MIGRATION_BODY.format(module=__name__, entity=entity.__name__)
        with open(revision_file, 'w') as file:
            file.write(generated[:generated.index('def upgrade():')] + body)
        return os.path.basename(revision_file)

    def _latest_version(self) -> str:
        with open(os.path.join(self.migrations, '.migration_ver')) as file:
            return file.read()

    def _database(self, name: str = 'acme.db'):
        engine = create_engine(f'sqlite:///{os.path.join(self.project_root, name)}')
        try:
            tables = set(inspect(engine).get_table_names())
            revisions = []
            if VERSION_TABLE in tables:
                with engine.connect() as connection:
                    revisions = connection.execute(text(f'SELECT version_num FROM {VERSION_TABLE}')).scalars().all()
            return tables, revisions
        finally:
            engine.dispose()

    def test_new_revisions_are_numbered_and_the_database_walks_through_them(self):
        first_revision = self._new_revision('create_widget', Widget)
        self.assertRegex(first_revision, r'^\d{4}-\d{2}-\d{2}_1_create_widget\.py$')
        self.assertEqual('1', self._latest_version())

        second_revision = self._new_revision('add_gadget', Gadget)
        self.assertRegex(second_revision, r'^\d{4}-\d{2}-\d{2}_2_add_gadget\.py$')
        self.assertEqual('2', self._latest_version())
        self.assertEqual([first_revision, second_revision], self._revision_files())

        self.assertIn('revision to `head`', self._migrate('--rev', 'head'))
        self.assertEqual(({Widget.__tablename__, Gadget.__tablename__, VERSION_TABLE}, ['2']), self._database())

        self._migrate('--rev', '-1')
        self.assertEqual(({Widget.__tablename__, VERSION_TABLE}, ['1']), self._database())

        self._migrate('--rev', '1')  # a positive number is a step up, not a revision
        self.assertEqual(({Widget.__tablename__, Gadget.__tablename__, VERSION_TABLE}, ['2']), self._database())

        self.assertIn('revision to `base`', self._migrate('--rev', 'base'))
        self.assertEqual(({VERSION_TABLE}, []), self._database())

    def test_new_without_a_name_creates_nothing(self):
        stdout = self._migrate('--rev', 'new')

        self.assertIn('--name parameter is mandatory when creating a new revision', stdout)
        self.assertEqual([], self._revision_files())
        self.assertFalse(os.path.exists(os.path.join(self.migrations, '.migration_ver')))

    def test_env_file_names_the_database_to_migrate(self):
        self._new_revision('create_widget', Widget)
        self._write('other.env', f'{DB_FILE_VARIABLE}=other.db\n')

        self._migrate('--rev', 'head', '--env_file', 'other.env')

        self.assertEqual(({Widget.__tablename__, VERSION_TABLE}, ['1']), self._database('other.db'))
        self.assertFalse(os.path.exists(os.path.join(self.project_root, 'acme.db')))

    def test_unknown_rev_runs_nothing(self):
        self._new_revision('create_widget', Widget)

        stdout = self._migrate('--rev', 'sideways')

        self.assertNotIn('revision to', stdout)
        self.assertFalse(os.path.exists(os.path.join(self.project_root, 'acme.db')))  # nothing connected to it
