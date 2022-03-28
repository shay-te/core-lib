from pymongo import MongoClient

from core_lib.data_layers.data.handler.data_handler import DataHandler


class MongoDBDataHandler(DataHandler):
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client

    def __enter__(self) -> MongoClient:
        return self.mongo_client

    def __exit__(self, exec_type, exec_value, traceback):
        pass
