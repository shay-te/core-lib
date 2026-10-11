"""Every skill is well-formed and routed: listed in AGENTS.md and in the generator template's copy, and every skill name used anywhere exists."""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, 'skills')
AGENTS_MD = os.path.join(REPO_ROOT, 'AGENTS.md')
TEMPLATE_AGENTS_MD = os.path.join(REPO_ROOT, 'core_lib_generator', 'template_core_lib', 'AGENTS.md')
NOT_IN_TEMPLATE = {'core-lib-new'}   # a generated lib already exists, so it is never told to bootstrap one
SKILL_NAME = re.compile(r'core-lib-[a-z]+(?:-[a-z]+)?')


def read(path: str) -> str:
    with open(path, encoding='utf-8') as file:
        return file.read()


def skill_names() -> list:
    return sorted(name for name in os.listdir(SKILLS_DIR) if os.path.isfile(os.path.join(SKILLS_DIR, name, 'SKILL.md')))


def routing_table_names(path: str) -> set:
    rows = [line for line in read(path).splitlines() if line.startswith('|') and 'SKILL.md' in line]
    return {match for row in rows for match in SKILL_NAME.findall(row.split('|')[2])}


class TestSkillsRouting(unittest.TestCase):

    def test_there_are_skills(self):
        self.assertIn('core-lib-service', skill_names())

    def test_front_matter_names_the_folder(self):
        for name in skill_names():
            front_matter = read(os.path.join(SKILLS_DIR, name, 'SKILL.md')).split('---')[1]
            self.assertIn(f'name: {name}\n', front_matter, name)
            self.assertRegex(front_matter, r'\ndescription: \S', name)

    def test_every_skill_is_in_the_agents_routing_table(self):
        self.assertEqual(set(skill_names()), routing_table_names(AGENTS_MD))

    def test_every_skill_but_new_is_in_the_template_routing_table(self):
        self.assertEqual(set(skill_names()) - NOT_IN_TEMPLATE, routing_table_names(TEMPLATE_AGENTS_MD))

    def test_every_referenced_skill_exists(self):
        sources = [AGENTS_MD, TEMPLATE_AGENTS_MD] + [os.path.join(SKILLS_DIR, name, 'SKILL.md') for name in skill_names()]
        referenced = {name for path in sources for name in SKILL_NAME.findall(read(path))}

        self.assertEqual(set(), referenced - set(skill_names()))
