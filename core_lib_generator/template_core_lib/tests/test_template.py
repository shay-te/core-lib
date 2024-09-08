import unittest
# template_core_lib_import
# template_test_imports
from core_lib.helpers.test import load_core_lib_config
from core_lib_generator.template_core_lib.tests.test_data.helpers.util import sync_create_start_core_lib


class TestTemplate(unittest.TestCase):
    def setUpClass(self):
        self.template_snake_core_lib = sync_create_start_core_lib()


# template_test_functions