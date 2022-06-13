from omegaconf import DictConfig
# template_alembic_imports
from core_lib.core_lib import CoreLib
# template_cache_handler_imports
# template_connections_imports
# template_da_imports
# template_service_imports


class Template(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf

# template_cache_handlers
# template_connections
# template_da_instances
# template_service_instances
# template_jobs_data_handlers
# template_load_jobs
# template_alembic_functions
