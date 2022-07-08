import io
import logging

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.connection.object_connection_registry import ObjectConnectionRegistry


class ObjectsDataAccess(DataAccess):
    def __init__(self, data_session_registry: ObjectConnectionRegistry):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data_session_registry = data_session_registry

    def get_object(self, bucket_name: str, key: str):
        data = io.BytesIO()
        with self.data_session_registry.get() as s3:
            s3.download_fileobj(bucket_name, key, data)
            return data

    def set_object(self, bucket_name: str, key: str, value):
        with open(value, "rb") as file:
            with self.data_session_registry.get() as session:
                session.upload_fileobj(file, bucket_name, key)
