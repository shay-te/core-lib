import os
import shutil
import tempfile
import unittest

from omegaconf import OmegaConf

from core_lib.connection.mongodb_connection_factory import MongoDBConnectionFactory
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
import mongomock


def _connect_to_sqlite(url: dict):
    conf = {
        'create_db': True,
        'log_queries': False,
        'session': {'pool_recycle': 3600, 'pool_pre_ping': False},
        'url': url,
    }
    return SqlAlchemyConnectionFactory(OmegaConf.create(conf))


def connect_to_mem_db():
    return _connect_to_sqlite({'protocol': 'sqlite'})


def connect_to_file_db(test_case: unittest.TestCase, file_path: str = None):
    # A sqlite FILE, removed when the test ends: unlike `sqlite://`, every thread sees one database and pool
    # events fire. Pass `file_path` for a second factory on the same file; `build_url` wants it relative.
    if file_path is None:
        directory = tempfile.mkdtemp()
        test_case.addCleanup(shutil.rmtree, directory, True)
        file_path = os.path.relpath(os.path.join(directory, 'test.db'))
    factory = _connect_to_sqlite({'protocol': 'sqlite', 'file': file_path})
    test_case.addCleanup(factory.engine.dispose)
    test_case.addCleanup(factory.connection.close)
    return factory


@mongomock.patch(servers=(('server.example.com', 27017), ))
def connect_to_mongo():
    conf = {
            'url': {
                'host': 'server.example.com',
                'port': 27017
            }
    }
    return MongoDBConnectionFactory(OmegaConf.create(conf))
