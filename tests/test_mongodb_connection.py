import unittest
import hydra
import mongomock

from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.helpers.config_instances import instantiate_config
from core_lib.connection.mongodb_connection_registry import MongoDBConnectionRegistry
hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path='./test_data/test_config')
configfile = "test_mongodb.yaml"
config = hydra.compose(configfile)


class TestMongoDBConnection(unittest.TestCase):

    @mongomock.patch(servers=((config.core_lib.mongodb.config.url.host, config.core_lib.mongodb.config.url.port), ))
    def test_instantiate(self):
        mongodb = instantiate_config(config.core_lib.mongodb)
        self.assertIsInstance(mongodb, MongoDBConnectionRegistry)
        with mongodb.get() as client:
            collection = client.testing_collection.example

            data = result_to_dict(collection.find())
            self.assertEqual(type(data), type([1, 2, 3]))

            inserted_id = collection.insert_one({'name': 'ansh', 'age': 18}).inserted_id
            entry = collection.find_one({'_id': inserted_id})
            self.assertEqual(entry['name'], 'ansh')
            self.assertEqual(entry['age'], 18)

            collection.update_one({'_id': inserted_id}, {'$set': {'name': "rohan"}})
            updated_entry = collection.find_one({'_id': inserted_id})
            self.assertEqual(updated_entry['name'], 'rohan')

            collection.delete_one({'_id': inserted_id})
            deleted_entry = collection.find_one({'_id': inserted_id})
            self.assertEqual(deleted_entry, None)
