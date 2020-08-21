from hydra.plugins import SearchPathPlugin
from hydra._internal.config_search_path import ConfigSearchPath


class CoreLibSearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path):
        assert isinstance(search_path, ConfigSearchPath)
        search_path.append("core-lib", "pkg://core_lib/config")
