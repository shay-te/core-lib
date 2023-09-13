import unittest

import hydra
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from core_lib.connection.elasticsearch_connection_registry import ElasticSearchConnectionRegistry
from core_lib.helpers.config_instances import instantiate_config

hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='./test_data/test_config')
configfile = "test_elasticsearch.yaml"
config = hydra.compose(configfile)


user_index_mappings = {
    "properties": {
        "username": {"type": "text", "analyzer": "standard"},
        "password": {"type": "text", "analyzer": "standard"},
    }
}

sample_data = [
    {"id": 1, "data": {"username": "test1", "password": "test1_pass", 'name': 'john'}},
    {"id": 2, "data": {"username": "test2", "password": "test2_pass", 'name': 'albert'}},
    {"id": 3, "data": {"username": "test3", "password": "test3_pass", 'name': 'john'}},
    {"id": 4, "data": {"username": "test4", "password": "test4_pass", 'name': 'lewis'}},
    {"id": 5, "data": {"username": "test5", "password": "test5_pass", 'name': 'albert'}},
    {"id": 6, "data": {"username": "test6", "password": "test6_pass", 'name': 'john'}},
]


class TestElasticsearchConnection(unittest.TestCase):
    def test_connection(self):
        connection = instantiate_config(config.core_lib.elasticsearch)
        self.assertIsInstance(connection, ElasticSearchConnectionRegistry)
        client = connection.client
        self.assertIsInstance(client, Elasticsearch)

        # Testing indexes
        self.assertIsNotNone(self.create_index(client))

        # Testing if adding data to elasticsearch works
        self.assertEqual(int(self.add_data_to_elasticsearch(client)[0]['count']), len(sample_data))

        # Testing if getting data from elasticsearch works
        query1_search_key = 'username'
        query1_search_value = 'test2'
        query1 = self.get_data_from_elasticsearch(client, query1_search_key, query1_search_value)
        self.assertEqual(int(query1['hits']['total']['value']), 1)
        self.assertEqual(query1['hits']['hits'][0]['_source'][query1_search_key], query1_search_value)

        query2_search_key = 'name'
        query2_search_value = 'john'
        query2 = self.get_data_from_elasticsearch(client, query2_search_key, query2_search_value)
        self.assertEqual(int(query2['hits']['total']['value']), 3)
        self.assertEqual(query2['hits']['hits'][0]['_source'][query2_search_key], query2_search_value)

        query3_search_key = 'name'
        query3_search_value = 'albert'
        query3 = self.get_data_from_elasticsearch(client, query3_search_key, query3_search_value)
        self.assertEqual(int(query3['hits']['total']['value']), 2)
        self.assertEqual(query3['hits']['hits'][0]['_source'][query3_search_key], query3_search_value)

        query4_search_key = 'name'
        query4_search_value = 'lewis'
        query4 = self.get_data_from_elasticsearch(client, query4_search_key, query4_search_value)
        self.assertEqual(int(query4['hits']['total']['value']), 1)
        self.assertEqual(query4['hits']['hits'][0]['_source'][query4_search_key], query4_search_value)

        self.delete_index(client)

    def add_data_to_elasticsearch(self, client):
        bulk_data = []
        for entry in sample_data:
            bulk_data.append(
                {
                    "_index": "user",
                    "_id": entry['id'],
                    "_source": entry['data']
                }
            )
        bulk(client, bulk_data)
        client.indices.refresh(index="user")
        return client.cat.count(index="user", format="json")

    def get_data_from_elasticsearch(self, client, key, value):
        return client.search(
            index='user',
            query={
                'match': {
                    key: {
                        'query': value
                    }
                }
            }
        )

    def create_index(self, client):
        client.indices.create(index='user', mappings=user_index_mappings)
        return client.indices.get(index='user')

    def delete_index(self, client):
        return client.indices.delete(index='user')
