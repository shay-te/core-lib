import boto3
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib
from core_lib.connection.object_connection_registry import ObjectConnectionRegistry
from examples.objects_core_lib.core_lib.data_layers.data_access.objects_data_access import ObjectsDataAccess
from examples.objects_core_lib.core_lib.data_layers.service.objects_service import ObjectsService


class ObjectsCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf.core_lib

        boto3_client = boto3.client(
            's3',
            region_name=self.config.s3.aws_region,
            aws_access_key_id=self.config.s3.aws_access_key_id,
            aws_secret_access_key=self.config.s3.aws_secret_access_key,
        )

        self.object = ObjectsService(ObjectsDataAccess(ObjectConnectionRegistry(boto3_client)))
