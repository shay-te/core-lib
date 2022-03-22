from omegaconf import DictConfig
from core_lib.core_lib import CoreLib

# template_cache_handler_imports
# template_data_handlers_imports
# template_da_imports


class TemplateCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf


# template_cache_handler
# template_data_handlers
# template_da_instances
# template_jobs_data_handlers
# template_load_jobs
