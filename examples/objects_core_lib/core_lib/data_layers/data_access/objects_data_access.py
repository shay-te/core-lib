import io
import logging
import tempfile
from sys import path

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data.handler.object_data_handler_registry import ObjectDataHandlerRegistry


class ObjectsDataAccess(DataAccess):
    def __init__(self, data_session_factory: ObjectDataHandlerRegistry):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data_session_factory = data_session_factory

    def get_object(self, bucket_name: str, object_name: str, key: str):
        with self.data_session_factory.get() as s3:
            with open(object_name, 'wb') as data:
                s3.download_fileobj(bucket_name, key, data)
                return data

    def set_object(self, bucket_name: str, value, key: str):
        with open(value, "rb") as file:
            with self.data_session_factory.get() as session:
                session.upload_fileobj(file, bucket_name, key)

