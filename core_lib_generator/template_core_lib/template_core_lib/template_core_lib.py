from omegaconf import DictConfig
from core_lib.core_lib import CoreLib


# template_da_imports
# template_entity_imports
# template_job_imports


class TemplateCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf

        # template_data_handlers
        # template_da_instances
