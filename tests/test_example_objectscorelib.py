import os
import unittest

import boto3
import hydra
from moto import mock_s3
from omegaconf import OmegaConf

from examples.objects_core_lib.core_lib.objects_core_lib import ObjectsCoreLib

# config_file = 'config.yaml'
# hydra.initialize(config_path='../examples/objects_core_lib/config')
# config = hydra.compose(config_file)
#
# objects_core_lib = ObjectsCoreLib(config.core_lib)


class ObjectsCoreLibTesting(ObjectsCoreLib):

    def __init__(self):
        conf = OmegaConf.create({"s3": {'aws_region': 'us-east-1'}})
        ObjectsCoreLib.__init__(self, conf)


class TestExamples(unittest.TestCase):
    @mock_s3
    def test_object_core_lib(self):
        upload_file_path = os.path.join(os.path.dirname(__file__), 'test_data\koala.jpeg')
        download_file_path = os.path.join(os.path.dirname(__file__), 'test_data\koalaAWS.jpeg')

        objects_core_lib = ObjectsCoreLibTesting()

        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket='mybucket')

        objects_core_lib.object.set_object('mybucket', upload_file_path, 'koala.jpeg')
        obj = objects_core_lib.object.get_object('mybucket', download_file_path, 'koala.jpeg')

        self.assertEqual(download_file_path, obj.name)
        self.assertTrue(os.path.isfile(obj.name))

