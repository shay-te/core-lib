import unittest
# template_core_lib_import
# template_test_imports
from core_lib.helpers.test import load_core_lib_config
# template_sync_create_core_lib_import


class TestTemplate(unittest.TestCase):
    def setUpClass(self):
        self.template_snake_core_lib = sync_create_start_core_lib()


# template_test_functions