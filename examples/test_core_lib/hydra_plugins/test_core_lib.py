from hydra.core.config_search_path import ConfigSearchPath
from hydra.plugins.search_path_plugin import SearchPathPlugin


class TestCoreLibSearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path: ConfigSearchPath) -> None:
        # Appends the search path for this plugin to the end of the search path
        search_path.append("test_core_lib_config", "pkg://config")
        search_path.append("test_core_lib_compose", "pkg://hydra_docker-compose.yaml")
