from omegaconf import DictConfig
from core_lib.core_lib import CoreLib
from examples.demo_core_lib.core_lib.demo_core_lib import DemoCoreLib
from examples.test_core_lib.core_lib.test_core_lib import TestCoreLib


class CombineCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        self.demo = DemoCoreLib(conf)
        self.test = TestCoreLib(conf)
