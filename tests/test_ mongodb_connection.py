import unittest
import hydra

from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.helpers.config_instances import instantiate_config
from core_lib.connection.mongodb_connection_registry import MongoDBConnectionRegistry


class TestMongoDBConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        hydra.core.global_hydra.GlobalHydra.instance().clear()
        hydra.initialize(config_path='./test_data/test_config')

    def test_instatiate(self):
        configfile = "test_mongodb.yaml"
        config = hydra.compose(configfile)
        mongodb = instantiate_config(config.core_lib.mongodb)
        self.assertIsInstance(mongodb, MongoDBConnectionRegistry)
        with mongodb.get() as client:

            def testing_crud():
                collection = client.testing_collection.example

                data = result_to_dict(collection.find())
                self.assertEqual(type(data), type([1, 2, 3]))

                inserted_id = collection.insert_one({'name': 'ansh', 'age': 18}).inserted_id
                entry = collection.find_one({'_id': inserted_id})
                self.assertEqual(entry['name'], 'ansh')
                self.assertEqual(entry['age'],  18)

                collection.update_one({'_id': inserted_id}, {'$set': {'name': "rohan"}})
                updated_entry = collection.find_one({'_id': inserted_id})
                self.assertEqual(updated_entry['name'], 'rohan')

                collection.delete_one({'_id': inserted_id})
                deleted_entry = collection.find_one({'_id': inserted_id})
                self.assertEqual(deleted_entry, None)

            testing_crud()