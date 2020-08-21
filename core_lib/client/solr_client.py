import json
from urllib.parse import urlencode

from core_lib.client.client_base import ClientBase


class SolrClient(ClientBase):

    def __init__(self, target_url):
        ClientBase.__init__(self, target_url)

    def data_import(self, core: str, command: str = None, abort: bool = None, clean: bool = None, commit: bool = None, debug: bool = None):
        params = {}
        if abort is not None:
            params['abort'] = json.dumps(abort)
        if clean is not None:
            params['clean'] = json.dumps(clean)
        if commit is not None:
            params['commit'] = json.dumps(commit)
        if debug is not None:
            params['debug'] = json.dumps(debug)
        params_str = ""
        if params:
            params_str = "&{}".format(urlencode(params))
        return self._get("solr/{core}/dataimport?command={command}{params}".format(core=core, command=command, params=params_str))

    def data_import_full(self, core: str, *args, **kwargs):
        return self.data_import(core, "full-import", *args, **kwargs)

    def data_import_delta(self, core: str, *args, **kwargs):
        return self.data_import(core, "delta-import", *args, **kwargs)

