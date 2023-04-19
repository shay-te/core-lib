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

            new_created_user = {'name': 'ansh', 'age': 18}
            user_id = collection.insert_one(new_created_user).inserted_id
            user_entry = collection.find_one({'_id': user_id})
            self.assertEqual(user_entry['name'], new_created_user['name'])
            self.assertEqual(user_entry['age'], new_created_user['age'])

            updated_user = {'name': 'rohan'}
            collection.update_one({'_id': user_id}, {'$set': updated_user})
            updated_entry = collection.find_one({'_id': user_id})
            self.assertEqual(updated_entry['name'], updated_user['name'])

            collection.delete_one({'_id': user_id})
            deleted_entry = collection.find_one({'_id': user_id})
            self.assertEqual(deleted_entry, None)

            data_in_db = result_to_dict(collection.find())
            self.assertEqual(len(data_in_db), 0)

            new_data = [{'name': 'albert'}, {'name': 'john'}, {'name': 'nick'}]
            collection.insert_many(new_data)
            current_data_in_db = result_to_dict(collection.find())
            self.assertEqual(len(current_data_in_db), len(new_data))
            self.assertEqual(current_data_in_db[0]['name'], new_data[0]['name'])
            self.assertEqual(current_data_in_db[1]['name'], new_data[1]['name'])
            self.assertEqual(current_data_in_db[2]['name'], new_data[2]['name'])

