import unittest
from core_lib_generator.core_lib_generator_from_yaml import CoreLibGenerator
from omegaconf import OmegaConf


class TestGenerateFromYaml(unittest.TestCase):
    def test_generating(self):
        # Change to path of your generated yaml here ↓
        config = OmegaConf.load('.\..\TestServerType.yaml')
        core_lib_generator = CoreLibGenerator(config)
        core_lib_generator.generate_tests()

if __name__ == '__main__':
    unittest.main()
