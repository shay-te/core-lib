import logging
import tempfile
from sys import path

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data.handler.object_data_handler_factory import ObjectDataHandlerFactory


class ObjectsDataAccess(DataAccess):

    def __init__(self, data_session_factory: ObjectDataHandlerFactory):
        DataAccess.__init__(self, data_session_factory)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_object(self, bucket_name: str, object_name: str):
        with tempfile.TemporaryFile() as file_name:
            with self.get_session() as s3:
                s3.download_fileobj(bucket_name, object_name, file_name)
                file_content = path(file_name).bytes()
        return file_content

    def set_object(self, bucket_name: str, value):
        with tempfile.TemporaryFile() as tmp_file:
            tmp_file.write(value.encode())
            with self.get_session() as session:
                session.upload_file(tmp_file.name, bucket_name, value)
