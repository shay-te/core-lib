from core_lib.data_layers.service.service import Service
from examples.objects_core_lib.core_lib.data_layers.data_access.objects_data_access import ObjectsDataAccess


class ObjectsService(Service):
    def __init__(self, data_access: ObjectsDataAccess):
        self.data_access = data_access

    def get_object(self, bucket_name: str, key: str):
        return self.data_access.get_object(bucket_name, key)

    def set_object(self, bucket_name: str, key: str, value):
        self.data_access.set_object(bucket_name, key, value)
