import os
import unittest
from time import sleep

from hydra.plugins.common.utils import configure_log

from core_lib.helpers.helpers import compose_configuration, compose_to_target_file
from core_lib.helpers.subprocess_execute import SubprocessExecute
from examples.combined_core_lib.combined_core_lib.combined_core_lib import CombineCoreLib

from examples.test_core_lib.test_core_lib import TestCoreLib
from tests.test_data.test_utils import DockerComposer
import pymysql

pymysql.install_as_MySQLdb()
configure_log(None, True)

os.environ["mysql_user"] = "test"
os.environ["mysql_password"] = "test"
os.environ["mysql_root_password"] = "test"
os.environ["mysql_db"] = "test"

example_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'examples'))
combined_core_lib_path = os.path.join(example_path, 'combined_core_lib')

docker_compose_file = os.path.join(combined_core_lib_path, 'docker-compose.yaml')

# Write `examples/combined_docker_compose.yaml` -> examples/combined_core_lib/docker-compose.yaml``
compose_to_target_file(os.path.join(example_path, 'combined_docker_compose.yaml'), docker_compose_file)





print('Stopping `docker-compose` for file: `{}`'.format(docker_compose_file))
docker_composer = DockerComposer()
out, err = docker_composer.down(docker_compose_file).communicate()
print('Starting `docker-compose` for file: `{}`'.format(docker_compose_file))
up_proc = docker_composer.up(docker_compose_file)
out, err = up_proc.communicate()


config_directory = os.path.join(combined_core_lib_path, 'config')
config_file = 'config.yaml'

# Write `examples/combined_config.yaml` -> examples/combined_core_lib/config/config.yaml``
compose_to_target_file(os.path.join(example_path, 'combined_config.yaml'), os.path.join(config_directory, config_file))

# Read generated docker compose file
config = compose_configuration(config_directory, config_file)




core_lib = CombineCoreLib(config.core_lib)


class TestCombinedExample(unittest.TestCase):

    def test_object_core_lib(self):
        bucket_name = 'my_backet'
        value = "my value"
        core_lib.data.object.set_object(bucket_name, value)
        self.assertEqual(core_lib.data.object.get_object(bucket_name), value)

    @classmethod
    def tearDownClass(cls):
        docker_composer.down(docker_compose_file).communicate()
        SubprocessExecute.kill(up_proc)
