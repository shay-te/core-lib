"""A pip install of core-lib carries everything it uses outside Python modules: the generator's whole
template, and the agent rulebook (AGENTS.md) with every skill, where a generated project's AGENTS.md says they are."""
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
TEMPLATE_DIR = os.path.join('core_lib_generator', 'template_core_lib')
TEMPLATE_AGENTS_MD = os.path.join(REPO_ROOT, TEMPLATE_DIR, 'AGENTS.md')

# Where an installed package keeps them: core_lib/agent_docs/AGENTS.md and core_lib/agent_docs/skills/<name>/SKILL.md.
SHIPPED_DIR = os.path.join('core_lib', 'agent_docs')


def skill_names() -> list:
    return sorted(name for name in os.listdir(SKILLS_DIR) if os.path.isfile(os.path.join(SKILLS_DIR, name, 'SKILL.md')))


def files_under(folder: str) -> list:
    return sorted(
        os.path.relpath(os.path.join(parent, name), folder)
        for parent, _, names in os.walk(folder)
        for name in names
        if '__pycache__' not in parent and not name.endswith('.pyc')
    )


def run_setup(*args):
    result = subprocess.run(
        [sys.executable, 'setup.py', '-q', *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=300
    )
    if result.returncode:
        raise AssertionError(result.stderr[-3000:])


class TestSetupBuild(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # build_py runs egg_info for the package data; --egg-base keeps its output out of the checkout.
        cls.build_folder = tempfile.mkdtemp()
        run_setup('egg_info', '--egg-base', cls.build_folder, 'build_py', '--build-lib', cls.build_folder)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.build_folder)

    def test_build_ships_the_whole_generator_template(self):
        # `core_lib generate` copies from these files; one missing file breaks it for every pip user.
        built = files_under(os.path.join(self.build_folder, TEMPLATE_DIR))

        self.assertEqual(files_under(os.path.join(REPO_ROOT, TEMPLATE_DIR)), built)

    def test_build_ships_the_rulebook_and_every_skill(self):
        shipped = os.path.join(self.build_folder, SHIPPED_DIR)

        self.assertTrue(filecmp.cmp(os.path.join(REPO_ROOT, 'AGENTS.md'), os.path.join(shipped, 'AGENTS.md'), shallow=False))
        self.assertEqual(skill_names(), sorted(os.listdir(os.path.join(shipped, 'skills'))))
        for name in skill_names():
            source = os.path.join(SKILLS_DIR, name, 'SKILL.md')
            self.assertTrue(filecmp.cmp(source, os.path.join(shipped, 'skills', name, 'SKILL.md'), shallow=False), name)

    def test_source_distribution_carries_the_rulebook_and_skills(self):
        # pip builds a PyPI sdist in isolation, from the sdist's files only.
        sdist_folder = tempfile.mkdtemp()
        try:
            run_setup('egg_info', '--egg-base', sdist_folder, 'sdist', '--dist-dir', sdist_folder)
            archive = next(name for name in os.listdir(sdist_folder) if name.endswith('.tar.gz'))
            with tarfile.open(os.path.join(sdist_folder, archive)) as sdist:
                members = {member.split('/', 1)[1] for member in sdist.getnames() if '/' in member}
        finally:
            shutil.rmtree(sdist_folder)

        expected = ['AGENTS.md'] + [f'skills/{name}/SKILL.md' for name in skill_names()]
        self.assertEqual([], [path for path in expected if path not in members])

    def test_generated_agents_md_points_at_the_installed_copy(self):
        with open(TEMPLATE_AGENTS_MD, encoding='utf-8') as agents_md:
            text = agents_md.read()

        pointer = f"os.path.join(os.path.dirname(core_lib.__file__), '{os.path.basename(SHIPPED_DIR)}')"
        self.assertTrue(pointer in text, f'the generated AGENTS.md has no {pointer}')
