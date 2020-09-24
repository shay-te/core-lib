# import os
#
# import boto3
# from dotenv import load_dotenv
# from core_lib.data_layers.data_access.handler.object_data_session_factory import ObjectDataHandlerFactory
# from examples.objects_core_lib.core_lib.data_layers.data_access.objects_data_access import ObjectsDataAccess
#
# current_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
#
# from pathlib import Path
# env_path = Path(os.path.join(current_path, 'test_data', 'examples.env'))
# load_dotenv(dotenv_path=env_path)
#
# print('Connecting with boto3...')
# handler = boto3.handler.Session()
# s3_client = handler.client(
#     service_name='s3',
#     region_name='ap-northeast-1',
#     aws_access_key_id='test',
#     aws_secret_access_key='test',
# )
# print('List Buckets.')
# print(s3_client.list_buckets())

# object_data_session_factory = ObjectDataHandlerFactory(s3_client)
# ob = ObjectsDataAccess(object_data_session_factory)
# ob.set_object('x', 'xxxx')
