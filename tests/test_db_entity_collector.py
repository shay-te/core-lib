"""`core_lib generate` asks about the entities of each database connection; each becomes an entity of the YAML."""
import unittest

from core_lib_generator.config_collectors.db_entity import generate_db_entity_template
from tests.test_data.test_utils import typed

CONNECTIONS = {'acme_db': {}, 'ledger_db': {}}   # the collector offers the connection names as a menu


def without_connection(entities: list) -> list:
    # `db_connection` is compared between entities instead: what it holds is checked by test_menu_choice_*.
    return [{key: value for key, value in entity.items() if key != 'db_connection'} for entity in entities]


class TestDbEntityCollector(unittest.TestCase):

    def test_each_column_type_asks_for_a_default_of_its_own_kind(self):
        with typed(
            '1', 'widget', '',                      # connection 1, entity name, add columns? [yes]
            'name', '', '', '', '',                 # VARCHAR [default type], no default, not nullable, another? [yes]
            'label', '2', 'acme', 'yes', '',        # VARCHAR with a default, nullable
            'stock', '1', '3', '', '',              # 1-INTEGER with a default
            'reorder_at', '1', '', 'yes', '',       # INTEGER without a default, nullable
            'active', '3', 'true', '', '',          # 3-BOOLEAN with a default
            'archived', '3', '', '', 'no',          # BOOLEAN without a default; no more columns
            '', '',                                 # soft delete? [no], another entity? [no]
        ):
            entities = generate_db_entity_template(CONNECTIONS)

        self.assertEqual([{
            'key': 'widget',
            'columns': [
                {'key': 'name', 'type': 'VARCHAR', 'default': None, 'nullable': False},
                {'key': 'label', 'type': 'VARCHAR', 'default': 'acme', 'nullable': True},
                {'key': 'stock', 'type': 'INTEGER', 'default': 3, 'nullable': False},
                {'key': 'reorder_at', 'type': 'INTEGER', 'default': None, 'nullable': True},
                {'key': 'active', 'type': 'BOOLEAN', 'default': True, 'nullable': False},
                {'key': 'archived', 'type': 'BOOLEAN', 'default': None, 'nullable': False},
            ],
            'is_soft_delete': False,
            'is_soft_delete_token': False,
        }], without_connection(entities))

    def test_soft_delete_token_is_asked_only_for_a_soft_delete_entity(self):
        with typed(
            '1', 'widget', 'no', 'yes', 'yes', 'yes',   # no columns; soft delete; token; another entity
            '1', 'gadget', 'no', 'yes', 'no', 'yes',    # soft delete without a token
            '1', 'sprocket', 'no', 'no', 'no',          # no soft delete: the next answer is "another entity?"
        ):
            entities = generate_db_entity_template(CONNECTIONS)

        self.assertEqual([
            {'key': 'widget', 'columns': [], 'is_soft_delete': True, 'is_soft_delete_token': True},
            {'key': 'gadget', 'columns': [], 'is_soft_delete': True, 'is_soft_delete_token': False},
            {'key': 'sprocket', 'columns': [], 'is_soft_delete': False, 'is_soft_delete_token': False},
        ], without_connection(entities))

    def test_menu_choice_decides_which_names_are_taken(self):
        with typed(
            '1', 'widget', 'yes', 'name', '', '', '', 'yes',
            'name', 'label', '', '', '', 'no',          # `name` is taken in this entity: asked again
            '', 'yes',
            '1', 'widget', 'gadget', 'no', '', 'yes',   # `widget` is taken on acme_db: asked again
            '2', 'widget', 'no', '', 'no',              # but free on ledger_db
        ):
            entities = generate_db_entity_template(CONNECTIONS)

        self.assertEqual(['widget', 'gadget', 'widget'], [entity['key'] for entity in entities])
        self.assertEqual(['name', 'label'], [column['key'] for column in entities[0]['columns']])
        acme_db_widget, acme_db_gadget, ledger_db_widget = (entity['db_connection'] for entity in entities)
        self.assertEqual(acme_db_widget, acme_db_gadget)
        self.assertNotEqual(acme_db_widget, ledger_db_widget)
