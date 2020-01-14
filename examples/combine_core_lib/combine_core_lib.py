from omegaconf import OmegaConf
from core_lib.core_lib import CoreLib
from examples.test_core_lib.test_core_lib import TestCoreLib
from examples.demo_core_lib.demo_core_lib import DemoCoreLib


class CombineCoreLib(CoreLib):

    def __init__(self, conf: OmegaConf):
        self.config = conf

        self.demo = DemoCoreLib(conf)
        self.test = TestCoreLib(conf)
