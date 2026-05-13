import unittest
from unittest.mock import MagicMock, patch

from omegaconf import OmegaConf

from core_lib.connection.elasticsearch_connection import ElasticSearchConnection
from core_lib.connection.elasticsearch_connection_factory import (
    ElasticSearchConnectionFactory,
)
from core_lib.connection.solr_connection import SolrConnection
from core_lib.client.solr_client import SolrClient
from core_lib.client.client_base import ClientBase


class TestElasticSearchConnection(unittest.TestCase):
    def test_context_manager_returns_client(self):
        client = MagicMock()
        conn = ElasticSearchConnection(client)
        with conn as c:
            self.assertIs(c, client)

    def test_exit_returns_nothing(self):
        conn = ElasticSearchConnection(MagicMock())
        self.assertIsNone(conn.__exit__(None, None, None))


class TestElasticSearchConnectionFactory(unittest.TestCase):
    def test_factory_creates_client_and_returns_connection(self):
        config = OmegaConf.create(
            {'url': {'protocol': 'http', 'host': 'localhost', 'port': 9200}}
        )
        with patch(
            'core_lib.connection.elasticsearch_connection_factory.Elasticsearch'
        ) as mock_es:
            fake_client = MagicMock()
            mock_es.return_value = fake_client
            factory = ElasticSearchConnectionFactory(config)
            self.assertIs(factory.client, fake_client)
            conn = factory.get()
            self.assertIsInstance(conn, ElasticSearchConnection)
            with conn as c:
                self.assertIs(c, fake_client)


class TestSolrConnection(unittest.TestCase):
    def test_context_manager_returns_client(self):
        client = MagicMock()
        conn = SolrConnection(client)
        with conn as c:
            self.assertIs(c, client)

    def test_exit_is_noop(self):
        conn = SolrConnection(MagicMock())
        self.assertIsNone(conn.__exit__(None, None, None))


class TestSolrClient(unittest.TestCase):
    def test_solr_client_initializes_base(self):
        client = SolrClient('http://localhost:8983/solr')
        self.assertEqual(client.base_url, 'http://localhost:8983/solr')
        self.assertIsInstance(client, ClientBase)
