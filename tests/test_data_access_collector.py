"""`core_lib generate` asks which DataAccess to write for each entity; each answer becomes a DataAccess of the YAML."""
import unittest

from core_lib_generator.config_collectors.data_access import generate_data_access_template
from tests.test_data.test_utils import typed


def entity(key: str, is_soft_delete: bool = False, is_soft_delete_token: bool = False) -> dict:
    return {
        'key': key,
        'db_connection': 'acme_db',
        'columns': [],
        'is_soft_delete': is_soft_delete,
        'is_soft_delete_token': is_soft_delete_token,
    }


ENTITIES = [entity('widget', True, True), entity('gadget', True), entity('sprocket')]


class TestDataAccessCollector(unittest.TestCase):

    def test_crud_question_follows_how_the_entity_deletes(self):
        # per DataAccess: entity number, name [Enter = <Entity>DataAccess], add a function? no,
        # the CRUD question, another DataAccess?
        with typed('1', '', 'no', 'yes', 'yes', '2', '', 'no', 'yes', 'yes', '3', '', 'no', 'yes', 'no'):
            data_accesses = generate_data_access_template(ENTITIES)

        self.assertEqual([
            {'key': 'WidgetDataAccess', 'entity': 'widget', 'functions': [], 'db_connection': 'acme_db',
             'is_crud': True, 'is_crud_soft_delete': True, 'is_crud_soft_delete_token': True},
            {'key': 'GadgetDataAccess', 'entity': 'gadget', 'functions': [], 'db_connection': 'acme_db',
             'is_crud': True, 'is_crud_soft_delete': True},
            {'key': 'SprocketDataAccess', 'entity': 'sprocket', 'functions': [], 'db_connection': 'acme_db',
             'is_crud': True},
        ], data_accesses)

    def test_declined_crud_writes_no_crud_flag(self):
        # The YAML generator picks the CRUD template by the PRESENCE of a flag, so a declined CRUD must leave it out.
        with typed('1', '', 'no', '', 'yes', '2', '', 'no', '', 'yes', '3', '', 'no', '', 'no'):
            data_accesses = generate_data_access_template(ENTITIES)

        self.assertEqual([
            {'key': 'WidgetDataAccess', 'entity': 'widget', 'functions': [], 'db_connection': 'acme_db'},
            {'key': 'GadgetDataAccess', 'entity': 'gadget', 'functions': [], 'db_connection': 'acme_db'},
            {'key': 'SprocketDataAccess', 'entity': 'sprocket', 'functions': [], 'db_connection': 'acme_db'},
        ], data_accesses)

    def test_taken_names_are_asked_again(self):
        with typed(
            '3', '', '',                                    # sprocket, default name, add a function [yes]
            'get_by_name', '', 'get_by_name', 'list_sprockets', 'no',   # a function name already taken is asked again
            'no', 'yes',                                    # no CRUD, another DataAccess
            '3', '',                                        # the default name is taken: no default, Enter asks again
            'SprocketDataAccess', 'sprocket archive',       # a taken name is asked again; the answer becomes PascalCase
            'no', 'no', 'no',
        ):
            data_accesses = generate_data_access_template(ENTITIES)

        self.assertEqual([
            {'key': 'SprocketDataAccess', 'entity': 'sprocket', 'db_connection': 'acme_db',
             'functions': [{'key': 'get_by_name'}, {'key': 'list_sprockets'}]},
            {'key': 'SprocketArchive', 'entity': 'sprocket', 'functions': [], 'db_connection': 'acme_db'},
        ], data_accesses)
