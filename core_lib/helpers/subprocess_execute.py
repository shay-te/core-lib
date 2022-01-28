import logging
import os
import signal
import subprocess
import threading
from contextlib import suppress
from subprocess import Popen
from time import sleep
from functools import partial

class SubprocessExecute(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def popen(self, *args, **kwargs):
        debug = False
        if 'log_output' in kwargs:
            debug = kwargs['log_output']
            del kwargs['log_output']

        if debug:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
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
        chunk_size = 1024
        for data in iter(partial(stream.read, chunk_size), b''):
            try:
                if not data:
                    break
            except BaseException as ex:
                self.logger.error(ex)

            self.logger.info('{}: {}'.format(name, data.decode('utf-8').strip()))

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
