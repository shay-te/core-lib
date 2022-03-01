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

    def get_object(self, bucket_name: str, object_name: str):
        file_object = io.BytesIO()
        with self.data_session_factory.get() as s3:
            s3.download_fileobj(bucket_name, object_name, file_object)
        return file_object

    def set_object(self, bucket_name: str, value):
        with open(value, "rb") as f:
            with self.data_session_factory.get() as session:
                session.upload_file(f.name, bucket_name, value)

