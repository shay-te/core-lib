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

        abs_path = os.path.abspath(file_path)
        self.assertTrue(os.path.exists(abs_path))

        with open(file_path, 'rb') as file:
            original_data = file.read()
            self.assertTrue(len(original_data) > 0)

        conn = boto3.resource(
            's3', region_name='us-east-1', aws_access_key_id="fake_access_key", aws_secret_access_key="fake_secret_key"
        )
        conn.create_bucket(Bucket=test_bucket)

        self.objects_core_lib.object.set_object(test_bucket, 'koala.jpeg', file_path)
        obj = self.objects_core_lib.object.get_object(test_bucket, 'koala.jpeg')
        obj.seek(0)
        s3_data = obj.read()

        self.assertTrue(len(s3_data) > 1000)
        self.assertTrue(b'\xff\xd8' in s3_data)
        self.assertTrue(b'\xff\xd9' in s3_data)
        self.assertTrue(original_data in s3_data)