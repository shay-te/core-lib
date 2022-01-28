from hydra.core.config_search_path import ConfigSearchPath
from hydra.plugins.search_path_plugin import SearchPathPlugin


class ObjectsCoreLibSearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path: ConfigSearchPath) -> None:
        search_path.append("objects_core_lib_config", "pkg://config")
        search_path.append("objects_core_lib_compose", "pkg://hydra_docker-compose.yaml")
