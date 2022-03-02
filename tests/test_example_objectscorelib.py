import os
import unittest

import boto3
from moto import mock_s3
from omegaconf import OmegaConf

from examples.objects_core_lib.core_lib.objects_core_lib import ObjectsCoreLib


class ObjectsCoreLibTesting(ObjectsCoreLib):

    def __init__(self):
        conf = OmegaConf.create({"s3": {'aws_region': 'us-east-1'}})
        ObjectsCoreLib.__init__(self, conf)


class TestExamples(unittest.TestCase):
    @mock_s3
    def test_object_core_lib(self):
        test_bucket = 'MyBucket'
        file_path = os.path.join(os.path.dirname(__file__), 'test_data/koala.jpeg')

        objects_core_lib = ObjectsCoreLibTesting()

        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket=test_bucket)

        objects_core_lib.object.set_object(test_bucket, 'koala.jpeg', file_path)
        obj = objects_core_lib.object.get_object(test_bucket, 'koala.jpeg')
        with open(file_path, 'rb') as file:
            self.assertEqual(file.read(), obj.getvalue())
