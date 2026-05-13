import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from omegaconf import OmegaConf

from core_lib.alembic.alembic import Alembic


def _build_config(script_dir: str, version_file_name: str = '.migration_ver'):
    return OmegaConf.create(
        {
            'core_lib': {
                'alembic': {
                    'version_table': 'alembic_version',
                    'script_location': script_dir,
                    'file_template': 'tmpl',
                    'timezone': None,
                    'truncate_slug_length': None,
                    'revision_environment': False,
                    'sourceless': False,
                    'output_encoding': 'utf-8',
                    'version_file_name': version_file_name,
                    'render_as_batch': False,
                },
                'data': {
                    'sqlalchemy': {
                        'config': {
                            'log_queries': False,
                            'url': {
                                'protocol': 'sqlite',
                                'username': None,
                                'password': None,
                                'host': None,
                                'port': None,
                                'file': None,
                            },
                        }
                    }
                },
            }
        }
    )


class TestAlembic(unittest.TestCase):
    def setUp(self):
        self.tmpdir_obj = tempfile.TemporaryDirectory()
        self.base_dir = self.tmpdir_obj.name
        self.rel_script = 'scripts'
        self.script_dir = os.path.join(self.base_dir, self.rel_script)
        os.makedirs(self.script_dir)
        self.addCleanup(self.tmpdir_obj.cleanup)

        self.engine_patch = patch('core_lib.alembic.alembic.create_engine')
        self.mock_create_engine = self.engine_patch.start()
        self.addCleanup(self.engine_patch.stop)
        self.mock_engine = MagicMock()
        self.mock_create_engine.return_value = self.mock_engine

    def _make_alembic(self, script_rel=None, version_file_name='.migration_ver'):
        config = _build_config(script_rel or self.rel_script, version_file_name=version_file_name)
        return Alembic(core_lib_path=self.base_dir, core_lib_config=config)

    def test_constructor_sets_options_and_creates_engine(self):
        alembic = self._make_alembic()
        self.assertEqual(alembic.script_location, self.script_dir)
        self.assertTrue(self.mock_create_engine.called)

    def test_constructor_raises_for_missing_script_dir(self):
        config = _build_config('does_not_exist')
        with self.assertRaises(ValueError):
            Alembic(core_lib_path=self.base_dir, core_lib_config=config)

    def test_constructor_raises_when_version_file_name_missing(self):
        with self.assertRaises(ValueError):
            self._make_alembic(version_file_name=None)

    def test_upgrade_runs_migration(self):
        alembic = self._make_alembic()
        with patch('core_lib.alembic.alembic.ScriptDirectory') as mock_sd, patch(
            'alembic.runtime.environment.EnvironmentContext'
        ) as mock_env_ctx:
            mock_env = MagicMock()
            mock_env_ctx.return_value.__enter__.return_value = mock_env
            alembic.upgrade('head')
            mock_env.run_migrations.assert_called_once()

    def test_downgrade_runs_migration(self):
        alembic = self._make_alembic()
        with patch('core_lib.alembic.alembic.ScriptDirectory') as mock_sd, patch(
            'alembic.runtime.environment.EnvironmentContext'
        ) as mock_env_ctx:
            mock_env = MagicMock()
            mock_env_ctx.return_value.__enter__.return_value = mock_env
            alembic.downgrade('base')
            mock_env.run_migrations.assert_called_once()

    def test_callback_branches_execute(self):
        alembic = self._make_alembic()
        with patch('core_lib.alembic.alembic.ScriptDirectory') as mock_sd, patch(
            'alembic.runtime.environment.EnvironmentContext'
        ) as mock_env_ctx:
            mock_env = MagicMock()
            mock_env_ctx.return_value.__enter__.return_value = mock_env

            mock_script_inst = MagicMock()
            mock_script_inst._upgrade_revs.return_value = ['up']
            mock_script_inst._downgrade_revs.return_value = ['down']

            mock_context = MagicMock()
            mock_context.script = mock_script_inst

            alembic.upgrade('head')
            upgrade_cb = mock_env_ctx.call_args[1].get('fn') or mock_env_ctx.call_args[0][2]
            self.assertEqual(upgrade_cb('rev', mock_context), ['up'])

            alembic.downgrade('base')
            downgrade_cb = mock_env_ctx.call_args[1].get('fn') or mock_env_ctx.call_args[0][2]
            self.assertEqual(downgrade_cb('rev', mock_context), ['down'])

    def test_history_invokes_command(self):
        alembic = self._make_alembic()
        with patch('core_lib.alembic.alembic.command') as mock_cmd:
            mock_cmd.history.return_value = 'history_result'
            self.assertEqual(alembic.history(), 'history_result')
            mock_cmd.history.assert_called_once_with(alembic.alembic_cfg)

    def test_create_migration_writes_version(self):
        alembic = self._make_alembic()
        with patch('core_lib.alembic.alembic.command') as mock_cmd, patch(
            'core_lib.alembic.alembic.ScriptDirectory'
        ) as mock_sd:
            mock_sd_inst = MagicMock()
            mock_sd_inst.walk_revisions.return_value = iter([MagicMock(), MagicMock()])
            mock_sd.from_config.return_value = mock_sd_inst

            alembic.create_migration('add_foo')

            mock_cmd.revision.assert_called_once()
            written_path = os.path.join(self.script_dir, '.migration_ver')
            self.assertTrue(os.path.exists(written_path))
            with open(written_path) as fh:
                self.assertEqual(fh.read(), '3')

    def test_create_migration_empty_name_raises(self):
        alembic = self._make_alembic()
        with self.assertRaises(ValueError):
            alembic.create_migration('')

    def test_read_version_counts_revisions(self):
        alembic = self._make_alembic()
        with patch('core_lib.alembic.alembic.ScriptDirectory') as mock_sd:
            mock_sd_inst = MagicMock()
            mock_sd_inst.walk_revisions.return_value = iter([MagicMock(), MagicMock(), MagicMock()])
            mock_sd.from_config.return_value = mock_sd_inst
            self.assertEqual(alembic._read_version(), 3)
