"""A pip install of core-lib carries the agent rulebook (AGENTS.md) and every skill, where a generated project's AGENTS.md says they are."""
import filecmp
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, 'skills')
TEMPLATE_AGENTS_MD = os.path.join(REPO_ROOT, 'core_lib_generator', 'template_core_lib', 'AGENTS.md')

# Where an installed package keeps them: core_lib/agent_docs/AGENTS.md and core_lib/agent_docs/skills/<name>/SKILL.md.
SHIPPED_DIR = os.path.join('core_lib', 'agent_docs')


def skill_names() -> list:
    return sorted(name for name in os.listdir(SKILLS_DIR) if os.path.isfile(os.path.join(SKILLS_DIR, name, 'SKILL.md')))


def run_setup(*args):
    result = subprocess.run(
        [sys.executable, 'setup.py', '-q', *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=300
    )
    if result.returncode:
        raise AssertionError(result.stderr[-3000:])


class TestSetupAgentDocs(unittest.TestCase):

    def setUp(self):
        self.output_folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.output_folder)

    def test_build_ships_the_rulebook_and_every_skill(self):
        # build_py runs egg_info for the package data; --egg-base keeps its output out of the checkout.
        run_setup('egg_info', '--egg-base', self.output_folder, 'build_py', '--build-lib', self.output_folder)
        shipped = os.path.join(self.output_folder, SHIPPED_DIR)

        self.assertTrue(filecmp.cmp(os.path.join(REPO_ROOT, 'AGENTS.md'), os.path.join(shipped, 'AGENTS.md'), shallow=False))
        self.assertEqual(skill_names(), sorted(os.listdir(os.path.join(shipped, 'skills'))))
        for name in skill_names():
            source = os.path.join(SKILLS_DIR, name, 'SKILL.md')
            self.assertTrue(filecmp.cmp(source, os.path.join(shipped, 'skills', name, 'SKILL.md'), shallow=False), name)

    def test_source_distribution_carries_them(self):
        # pip builds a PyPI sdist in isolation, from the sdist's files only.
        run_setup('egg_info', '--egg-base', self.output_folder, 'sdist', '--dist-dir', self.output_folder)
        archive = next(name for name in os.listdir(self.output_folder) if name.endswith('.tar.gz'))
        with tarfile.open(os.path.join(self.output_folder, archive)) as sdist:
            members = {member.split('/', 1)[1] for member in sdist.getnames() if '/' in member}

        expected = ['AGENTS.md'] + [f'skills/{name}/SKILL.md' for name in skill_names()]
        self.assertEqual([], [path for path in expected if path not in members])

    def test_generated_agents_md_points_at_the_installed_copy(self):
        with open(TEMPLATE_AGENTS_MD, encoding='utf-8') as agents_md:
            text = agents_md.read()

        pointer = "os.path.join(os.path.dirname(core_lib.__file__), 'agent_docs')"
        self.assertTrue(pointer in text, f'the generated AGENTS.md has no {pointer}')
        # The old pointer, to a package that shipped neither file.
        self.assertFalse('or in the\ninstalled `core-lib` package' in text, 'the old pointer is still there')
