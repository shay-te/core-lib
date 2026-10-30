"""`core_lib generate` asks which services to write over the DataAccesses; each answer becomes a service of the YAML."""
import unittest

from core_lib_generator.config_collectors.service import generate_service_template
from tests.test_data.test_utils import typed

DATA_ACCESSES = [
    {'key': 'WidgetDataAccess', 'entity': 'widget', 'functions': []},
    {'key': 'GadgetDataAccess', 'entity': 'gadget', 'functions': []},
]


class TestServiceCollector(unittest.TestCase):

    def test_with_a_cache_each_function_is_asked_whether_to_cache(self):
        with typed(
            '1', 'widget service', '',                          # DataAccess 1, service name, add a function [yes]
            'get_by_name', 'yes', 'yes', 'CACHE_WIDGET', '', 'yes',   # @ResultToDict, cached, not invalidating
            'get_by_name', 'rename_widget', '', 'yes', 'CACHE_WIDGET', 'yes', 'yes',   # taken name asked again
            'count_widgets', '', 'no', 'no',                    # not cached: no key and no invalidate question
            'no',                                               # another service
        ):
            services = generate_service_template(DATA_ACCESSES, True)

        self.assertEqual([{
            'key': 'WidgetService',
            'data_access': 'WidgetDataAccess',
            'functions': [
                {'key': 'get_by_name', 'result_to_dict': True, 'cache_key': 'CACHE_WIDGET', 'cache_invalidate': False},
                {'key': 'rename_widget', 'result_to_dict': False, 'cache_key': 'CACHE_WIDGET',
                 'cache_invalidate': True},
                {'key': 'count_widgets', 'result_to_dict': False},
            ],
        }], services)

    def test_without_a_cache_nothing_is_asked_about_caching(self):
        with typed(
            '1', 'WidgetService', '', 'count_widgets', '', 'no',   # @ResultToDict [no], then "another function?"
            'yes',
            '2', 'WidgetService', 'GadgetService', 'no',           # a taken service name is asked again; no functions
            'no',
        ):
            services = generate_service_template(DATA_ACCESSES, False)

        self.assertEqual([
            {'key': 'WidgetService', 'data_access': 'WidgetDataAccess',
             'functions': [{'key': 'count_widgets', 'result_to_dict': False}]},
            {'key': 'GadgetService', 'data_access': 'GadgetDataAccess', 'functions': []},
        ], services)
