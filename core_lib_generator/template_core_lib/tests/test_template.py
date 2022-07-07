import unittest
# template_core_lib_import
# template_test_imports
from core_lib.helpers.test import load_core_lib_config


class TestTemplate(unittest.TestCase):
    def setUpClass(self):
        config = load_core_lib_config('./test_data/test_config/config.yaml')
        self.template_snake_core_lib = TemplateCoreLib(config)

# template_test_functions
