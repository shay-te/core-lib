from omegaconf import DictConfig
from pysolr import Solr

from core_lib.connection.connection_factory import ConnectionFactory
from core_lib.connection.solr_connection import SolrConnection
from core_lib.data_layers.data.data_helpers import build_url


class SolrConnectionFactory(ConnectionFactory):
    # pysolr defaults to 60s. A hung Solr would hold a request thread for a full minute, so a slow
    # index becomes an app-wide outage; bound it instead.
    DEFAULT_TIMEOUT_SECONDS = 15

    def __init__(self, config: DictConfig):
        # 1. fetch
        url_config = config.url
        always_commit = config.always_commit
        username = config.get('username')
        password = config.get('password')
        timeout = config.get('timeout')

        # 2. validate / normalize
        # Credentials are OPTIONAL (Solr may run without basic auth) but they live BESIDE `url`,
        # not inside it — so `build_url(**config.url)` never sees them. Passing them here is what
        # stops every query returning 401 once `solr_sync_password.sh` sets blockUnknown=true;
        # without it the alias healthcheck stays green while the whole app is locked out of search.
        auth = (username, password) if username else None
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT_SECONDS

        # 3. use
        self._config = config
        self._solr_client = Solr(build_url(**url_config), always_commit=always_commit,
                                 auth=auth, timeout=timeout)

    @property
    def client(self) -> Solr:
        return self._solr_client

    def get(self, *args, **kwargs) -> SolrConnection:
        return SolrConnection(self._solr_client)
