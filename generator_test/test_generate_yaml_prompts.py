import os
import tempfile
import unittest
from unittest.mock import patch

from omegaconf import OmegaConf

import core_lib_generator.core_lib_config_generate_yaml as yaml_gen_module
from core_lib_generator.core_lib_config_generate_yaml import ServerType, generate_core_lib_yaml


def _inputs(core_lib_name='', cache='no', db='no', job='no', server_type='', setup='no'):
    """Build an ordered input sequence for generate_core_lib_yaml() with all options off."""
    return [
        core_lib_name,  # prompt_str  → name  ('' = accept default 'MyCoreLib')
        cache,          # prompt_yes_no → want_cache
        db,             # prompt_yes_no → want_db (inside _get_data_layers_config)
        job,            # prompt_yes_no → want_job
        server_type,    # prompt_enum  → server_type ('' = accept default NOSERVER)
        setup,          # prompt_yes_no → want_setup
    ]


class TestGenerateCoreLibYamlPrompts(unittest.TestCase):
    def setUp(self):
        yaml_gen_module.config.clear()
        yaml_gen_module.config['data'] = []
        yaml_gen_module.config['cache'] = []
        yaml_gen_module.config['jobs'] = []
        yaml_gen_module.setup.clear()
        yaml_gen_module.setup['data'] = {}
        yaml_gen_module.env.clear()
        yaml_gen_module.data_layers.clear()
        yaml_gen_module.data_layers['data'] = []
        yaml_gen_module.data_layers['data_access'] = []
        yaml_gen_module.data_layers['service'] = []

    def _run(self, inputs):
        it = iter(inputs)
        orig = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                with patch('builtins.input', side_effect=lambda _: next(it)):
                    yaml_file = generate_core_lib_yaml()
                return OmegaConf.load(os.path.join(tmpdir, yaml_file))
            finally:
                os.chdir(orig)

    # ── server type ───────────────────────────────────────────────────────────

    def test_server_type_flask(self):
        cfg = self._run(_inputs(server_type=str(ServerType.FLASK.value)))
        self.assertEqual(cfg.core_lib.server_type, ServerType.FLASK.value)

    def test_server_type_django(self):
        cfg = self._run(_inputs(server_type=str(ServerType.DJANGO.value)))
        self.assertEqual(cfg.core_lib.server_type, ServerType.DJANGO.value)

    def test_server_type_noserver_explicit(self):
        cfg = self._run(_inputs(server_type=str(ServerType.NOSERVER.value)))
        self.assertEqual(cfg.core_lib.server_type, ServerType.NOSERVER.value)

    def test_server_type_noserver_default(self):
        # empty input → prompt_enum accepts the default (NOSERVER=3)
        cfg = self._run(_inputs(server_type=''))
        self.assertEqual(cfg.core_lib.server_type, ServerType.NOSERVER.value)

    # ── yaml structure ────────────────────────────────────────────────────────

    def test_core_lib_name_default(self):
        cfg = self._run(_inputs())
        self.assertEqual(cfg.core_lib.name, 'MyCoreLib')

    def test_core_lib_name_custom(self):
        cfg = self._run(_inputs(core_lib_name='my_cool_lib'))
        self.assertEqual(cfg.core_lib.name, 'MyCoolLib')

    def test_yaml_has_required_keys(self):
        cfg = self._run(_inputs())
        core_lib = cfg.core_lib
        for key in ('name', 'server_type', 'connections', 'caches', 'jobs', 'entities', 'data_accesses', 'services'):
            self.assertIn(key, core_lib)

    def test_no_db_empty_connections(self):
        cfg = self._run(_inputs(db='no'))
        self.assertEqual(len(cfg.core_lib.connections), 0)

    def test_no_cache_empty_caches(self):
        cfg = self._run(_inputs(cache='no'))
        self.assertEqual(len(cfg.core_lib.caches), 0)

    def test_no_job_empty_jobs(self):
        cfg = self._run(_inputs(job='no'))
        self.assertEqual(len(cfg.core_lib.jobs), 0)


if __name__ == '__main__':
    unittest.main()
