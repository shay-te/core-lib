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
            self.assertIsInstance(data, list)

            test_insert_entry = {'name': 'ansh', 'age': 18}
            user_id = collection.insert_one(test_insert_entry).inserted_id
            user_entry = collection.find_one({'_id': user_id})
            self.assertEqual(user_entry['name'], test_insert_entry['name'])
            self.assertEqual(user_entry['age'], test_insert_entry['age'])

            test_update_entry = {'name': 'rohan'}
            collection.update_one({'_id': user_id}, {'$set': test_update_entry})
            updated_entry = collection.find_one({'_id': user_id})
            self.assertEqual(updated_entry['name'], test_update_entry['name'])

            collection.delete_one({'_id': user_id})
            deleted_entry = collection.find_one({'_id': user_id})
            self.assertEqual(deleted_entry, None)
