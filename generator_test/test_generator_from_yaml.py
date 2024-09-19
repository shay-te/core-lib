import unittest
from core_lib_generator.core_lib_generator_from_yaml import CoreLibGenerator
from omegaconf import OmegaConf


class TestGenerateFromYaml(unittest.TestCase):
    def test_generate_all(self):
        # Change to path of your generated yaml here ↓
        config = OmegaConf.load('.\..\OrenCoreLib.yaml')
        core_lib_generator = CoreLibGenerator(config)
        core_lib_generator.run_all()

    def test_generating_tests(self):
        # Change to path of your generated yaml here ↓
        config = OmegaConf.load('.\..\OrensCoreLib.yaml')
        core_lib_generator = CoreLibGenerator(config)
        core_lib_generator.generate_tests()

if __name__ == '__main__':
    unittest.main()
