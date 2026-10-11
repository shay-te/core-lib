"""Alembic.create_migration refuses an empty name with ValueError and numbers real revisions from 1."""
import os
import shutil
import tempfile
import unittest

from omegaconf import OmegaConf

from core_lib.alembic.alembic import Alembic

TEMPLATE_MIGRATIONS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'core_lib_generator', 'template_core_lib', 'template_core_lib', 'data_layers', 'data', 'db', 'migrations',
)
VERSION_FILE_NAME = '.migration_ver'


class TestAlembicCreateMigration(unittest.TestCase):

    def setUp(self):
        self.core_lib_path = tempfile.mkdtemp()
        self.migrations_path = os.path.join(self.core_lib_path, 'migrations')
        os.makedirs(os.path.join(self.migrations_path, 'versions'))
        shutil.copy(os.path.join(TEMPLATE_MIGRATIONS, 'script.py.mako'), self.migrations_path)
        config = OmegaConf.create({
            'core_lib': {
                'alembic': {
                    'script_location': 'migrations',
                    'file_template': '%%(rev)s_%%(slug)s',
                    'version_table': 'acme_alembic_version',
                    'version_file_name': VERSION_FILE_NAME,
                    'render_as_batch': False,
                },
                'data': {'sqlalchemy': {'config': {'log_queries': False, 'url': {'protocol': 'sqlite'}}}},
            },
        })
        self.alembic = Alembic(self.core_lib_path, config)

    def tearDown(self):
        shutil.rmtree(self.core_lib_path)

    def _revision_files(self):
        return sorted(name for name in os.listdir(os.path.join(self.migrations_path, 'versions')) if name.endswith('.py'))

    def test_empty_name_raises_value_error_and_writes_nothing(self):
        for empty_name in ('', None):
            with self.assertRaisesRegex(ValueError, 'Migration name must be set'):
                self.alembic.create_migration(empty_name)
        self.assertEqual([], self._revision_files())
        self.assertFalse(os.path.exists(os.path.join(self.migrations_path, VERSION_FILE_NAME)))

    def test_revisions_are_numbered_from_one(self):
        self.alembic.create_migration('create widget')
        self.alembic.create_migration('add widget color')

        self.assertEqual(['1_create_widget.py', '2_add_widget_color.py'], self._revision_files())
        with open(os.path.join(self.migrations_path, VERSION_FILE_NAME)) as version_file:
            self.assertEqual('2', version_file.read())
