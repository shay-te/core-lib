import boto3
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib
from core_lib.data_layers.data_access.sessions.object_data_session import ObjectDataSession
from examples.objects_core_lib.data_layers.data_access.objects_data_access import ObjectsDataAccess
from examples.test_core_lib.data_layers.service.user_service import ObjectsService


class ObjectsCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        boto3_client = boto3.client(
            's3',
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key,
            aws_session_token=self.config.aws_session_token
        )

        db_data_session = ObjectDataSession(boto3_client)
        self.object = ObjectsService(ObjectsDataAccess([db_data_session]))
