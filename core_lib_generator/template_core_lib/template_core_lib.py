from omegaconf import DictConfig
from core_lib.core_lib import CoreLib


class TemplateCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf