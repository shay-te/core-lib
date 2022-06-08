import unittest

import hydra
from pysolr import Solr

from core_lib.data_layers.data.handler.solr_data_handler import SolrDataHandler
from core_lib.data_layers.data.handler.solr_data_handler_registry import SolrDataHandlerRegistry
from core_lib.helpers.config_instances import instantiate_config


class TestSolrHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        hydra.core.global_hydra.GlobalHydra.instance().clear()
        hydra.initialize(config_path='./test_data/test_config')

    def test_instantiate(self):
        config_file = 'test_solr.yaml'
        config = hydra.compose(config_file)
        solr = instantiate_config(config.core_lib.solr)
        self.assertIsInstance(solr, SolrDataHandlerRegistry)
        self.assertIsInstance(solr.client, Solr)
        self.assertIsInstance(solr.get(), SolrDataHandler)

