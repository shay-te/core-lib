from core_lib.helpers.subprocess_execute import SubprocessExecute


class DockerComposer(object):

    def up(self, compose_file):
        return SubprocessExecute().popen(['docker-compose', '-f', compose_file, 'up', '-d'], shell=False)

    def down(self, compose_file):
        return SubprocessExecute().popen(['docker-compose', '-f', compose_file, 'down'], shell=False)
