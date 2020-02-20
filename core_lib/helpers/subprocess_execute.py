import logging
import os
import signal
import subprocess
import threading
from contextlib import suppress
from subprocess import Popen
from time import sleep


class SubprocessExecute(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def popen(self, *args, **kwargs):
        debug = True if 'log_output' in kwargs and kwargs['log_output'] else False
        if debug:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE

            del kwargs['log_output']
        else:
            if 'stdout' in kwargs:
                del kwargs['stdout']
            if 'stderr' in kwargs:
                del kwargs['stderr']

        process = Popen(*args, **kwargs)
        sleep(0.6)  # wait for server to start
        poll = process.poll()
        if poll is None:
            if debug:
                if process.stdout:
                    threading.Thread(target=self.__output_reader, args=('STDOUT', process.stdout,)).start()
                if process.stderr:
                    threading.Thread(target=self.__output_reader, args=('STDERR', process.stderr,)).start()
            return process
        else:
            out, err = process.communicate()
            raise OSError('{}\n{}'.format(out.decode("utf-8"), err.decode("utf-8")))

    def __output_reader(self, name: str, stream):
        try:
            for line in iter(stream.readline, b''):
                self.logger.info('{}: {}'.format(name, line.strip().decode('utf-8')))
        except BaseException as ex:
            self.logger.error(ex)

    @staticmethod
    def kill(process):
        if process:
            pid = process.pid
            with suppress(Exception):
                os.kill(pid, signal.SIGINT)
                os.kill(pid, signal.SIGTERM)

            process.poll()
            process.kill()
            process.terminate()
            if process.poll() is None:
                with suppress(Exception):
                    process.stdout.close()
                    process.stderr.close()
