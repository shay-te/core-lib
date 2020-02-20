import boto3
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib
from core_lib.data_layers.data_access.sessions.object_data_session import ObjectDataSession
from core_lib.data_layers.data_access.sessions.object_data_session_factory import ObjectDataSessionFactory
from examples.objects_core_lib.data_layers.data_access.objects_data_access import ObjectsDataAccess
from examples.objects_core_lib.data_layers.service.objects_service import ObjectsService


class ObjectsCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        boto3_client = boto3.client('s3',
                                    aws_access_key_id=self.config.s3.aws_access_key_id,
                                    aws_secret_access_key=self.config.s3.aws_secret_access_key,
                                    aws_session_token=self.config.s3.aws_session_token)

        object_data_session_factory = ObjectDataSessionFactory(boto3_client)
        self.object = ObjectsService(ObjectsDataAccess(object_data_session_factory))

