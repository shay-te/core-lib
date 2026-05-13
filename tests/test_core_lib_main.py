import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from core_lib import core_lib_main


class TestHelpers(unittest.TestCase):
    def test_list_to_string(self):
        self.assertEqual(core_lib_main.list_to_string(['a', 'b', 'c']), 'a b c ')
        self.assertEqual(core_lib_main.list_to_string([]), '')

    def test_get_rev_options(self):
        opts = core_lib_main.get_rev_options()
        self.assertIn('head', opts)
        self.assertIn('base', opts)
        self.assertIn('new', opts)
        self.assertIn('+1', opts)
        self.assertIn('-1', opts)
        self.assertIn('+10', opts)
        self.assertIn('-10', opts)
        self.assertNotIn('0', opts)
        self.assertNotIn('+0', opts)


class TestLoadConfig(unittest.TestCase):
    def test_load_config(self):
        with patch('core_lib.core_lib_main.initialize'), patch(
            'core_lib.core_lib_main.compose'
        ) as mock_compose:
            mock_compose.return_value = {'core_lib_module': 'core_lib'}
            result = core_lib_main.load_config()
            self.assertEqual(result, {'core_lib_module': 'core_lib'})


class TestMainGroup(unittest.TestCase):
    def test_main_group_runs(self):
        runner = CliRunner()
        result = runner.invoke(core_lib_main.main, [])
        self.assertEqual(result.exit_code, 0)

    def test_main_callback_directly(self):
        self.assertIsNone(core_lib_main.main.callback())


class TestGenerateCommand(unittest.TestCase):
    def test_generate_with_existing_yaml(self):
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp:
            tmp.write(b'placeholder: yes\n')
            yaml_path = tmp.name
        try:
            with patch(
                'core_lib.core_lib_main.hydra.core.global_hydra.GlobalHydra'
            ), patch('core_lib.core_lib_main.initialize_config_dir'), patch(
                'core_lib.core_lib_main.hydra.compose', return_value={'k': 'v'}
            ), patch(
                'core_lib.core_lib_main.CoreLibGenerator'
            ) as mock_gen:
                result = runner.invoke(core_lib_main.generate, ['--yaml', yaml_path])
                self.assertEqual(result.exit_code, 0)
                mock_gen.return_value.run_all.assert_called_once()
        finally:
            os.unlink(yaml_path)

    def test_generate_with_missing_yaml(self):
        runner = CliRunner()
        result = runner.invoke(
            core_lib_main.generate, ['--yaml', '/nonexistent_yaml_12345.yaml']
        )
        self.assertIn('yaml file was not found', result.output)

    def test_generate_without_yaml_creates_one(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = os.path.join(tmpdir, 'auto.yaml')
            with open(yaml_path, 'w') as fh:
                fh.write('placeholder: yes\n')
            with patch(
                'core_lib.core_lib_main.generate_core_lib_yaml',
                return_value=yaml_path,
            ), patch.object(os, 'getcwd', return_value=''), patch(
                'core_lib.core_lib_main.hydra.core.global_hydra.GlobalHydra'
            ), patch(
                'core_lib.core_lib_main.initialize_config_dir'
            ), patch(
                'core_lib.core_lib_main.hydra.compose', return_value={'k': 'v'}
            ), patch(
                'core_lib.core_lib_main.CoreLibGenerator'
            ) as mock_gen:
                result = runner.invoke(core_lib_main.generate, [])
                self.assertEqual(result.exit_code, 0)
                mock_gen.return_value.run_all.assert_called_once()


class TestMigrateCommand(unittest.TestCase):
    def _patches(self, alembic_mock=None):
        return [
            patch('core_lib.core_lib_main.load_dotenv'),
            patch('core_lib.core_lib_main.load_config', return_value=MagicMock(core_lib_module='core_lib')),
            patch('core_lib.core_lib_main.Alembic', return_value=alembic_mock or MagicMock()),
        ]

    def _run_migrate(self, args, alembic_mock=None):
        runner = CliRunner()
        ps = self._patches(alembic_mock)
        for p in ps:
            p.start()
        try:
            return runner.invoke(core_lib_main.migrate, args)
        finally:
            for p in ps:
                p.stop()

    def test_migrate_head(self):
        m = MagicMock()
        result = self._run_migrate(['--rev', 'head'], m)
        self.assertEqual(result.exit_code, 0)
        m.upgrade.assert_called_once_with('head')

    def test_migrate_base(self):
        m = MagicMock()
        result = self._run_migrate(['--rev', 'base'], m)
        self.assertEqual(result.exit_code, 0)
        m.downgrade.assert_called_once_with('base')

    def test_migrate_positive_int(self):
        m = MagicMock()
        result = self._run_migrate(['--rev', '2'], m)
        self.assertEqual(result.exit_code, 0)
        m.upgrade.assert_called_once_with('+2')

    def test_migrate_negative_int(self):
        m = MagicMock()
        result = self._run_migrate(['--rev', '-3'], m)
        self.assertEqual(result.exit_code, 0)
        m.downgrade.assert_called_once_with('-3')

    def test_migrate_new_with_name(self):
        m = MagicMock()
        result = self._run_migrate(['--rev', 'new', '--name', 'my_mig'], m)
        self.assertEqual(result.exit_code, 0)
        m.create_migration.assert_called_once_with('my_mig')

    def test_migrate_new_without_name(self):
        m = MagicMock()
        result = self._run_migrate(['--rev', 'new'], m)
        self.assertEqual(result.exit_code, 0)
        m.create_migration.assert_not_called()
        self.assertIn('--name', result.output)
