import os
import unittest

import boto3
from moto import mock_s3

from core_lib.helpers.test import load_core_lib_config
from examples.objects_core_lib.core_lib.objects_core_lib import ObjectsCoreLib


@mock_s3
class TestExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = load_core_lib_config('../examples/objects_core_lib/config')
        cls.objects_core_lib = ObjectsCoreLib(config)

    def test_object_core_lib(self):
        test_bucket = 'MyBucket'
        file_path = os.path.join(os.path.dirname(__file__), 'test_data/koala.jpeg')

        conn = boto3.resource(
            's3', region_name='us-east-1', aws_access_key_id="fake_access_key", aws_secret_access_key="fake_secret_key"
        )
        conn.create_bucket(Bucket=test_bucket)

        self.objects_core_lib.object.set_object(test_bucket, 'koala.jpeg', file_path)
        obj = self.objects_core_lib.object.get_object(test_bucket, 'koala.jpeg')
        with open(file_path, 'rb') as file:
            self.assertEqual(file.read(), obj.getvalue())
