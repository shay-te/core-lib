from pymongo import MongoClient
from core_lib.connection.connection import Connection


class MongoDBConnection(Connection):
    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client

    def __enter__(self) -> MongoClient:
        return self.mongo_client

    def __exit__(self, exec_type, exec_value, traceback):
        pass
