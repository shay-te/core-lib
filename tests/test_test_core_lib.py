import os
import unittest
from time import sleep

from hydra.plugins.common.utils import configure_log

from core_lib.helpers.helpers import compose_configuration
from core_lib.helpers.subprocess_execute import SubprocessExecute
from examples.test_core_lib.test_core_lib import TestCoreLib
from tests.test_data.test_utils import DockerComposer
import pymysql

pymysql.install_as_MySQLdb()
configure_log(None, False)

example_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'examples')
docker_compose_file = os.path.normpath(os.path.join(example_path, 'test_core_lib_docker_compose.yaml'))

docker_composer = DockerComposer()
process = docker_composer.up(docker_compose_file)
print('starting docker compose for file "{}"'.format(docker_compose_file))
print('sleep 10 seconds till docker compose up. prior to test please run: "docker-compose -f {} pull"'.format(docker_compose_file))
sleep(10)
test_core_lib = TestCoreLib(compose_configuration(os.path.join(example_path, 'config'), 'test_core_lib.yaml').core_lib)


class TestTestCoreLib(unittest.TestCase):

    def test_declaration(self):
        self.assertEqual(test_core_lib.test.test_1.get_by_id(1), 1)

    @classmethod
    def tearDownClass(cls):
        docker_composer.down(docker_compose_file)
        SubprocessExecute.kill(process)
