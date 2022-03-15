from omegaconf import DictConfig
from core_lib.core_lib import CoreLib


class MyCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
