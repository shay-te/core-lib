import boto3
from boto import Config
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib
from core_lib.data_layers.data.handler.object_data_handler_factory import ObjectDataHandlerFactory
from examples.objects_core_lib.core_lib.data_layers.data_access.objects_data_access import ObjectsDataAccess
from examples.objects_core_lib.core_lib.data_layers.service.objects_service import ObjectsService


class ObjectsCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        boto3_client = boto3.client('s3',
                                    region_name=self.config.s3.aws_region,
                                    config=Config())

        object_data_session_factory = ObjectDataHandlerFactory(boto3_client)
        self.object = ObjectsService(ObjectsDataAccess(object_data_session_factory))

