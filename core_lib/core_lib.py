import logging
from typing import List

from hydra.utils import instantiate
from omegaconf import DictConfig

from core_lib.cache.cache_factory import CacheFactory
from core_lib.core_lib_listener import CoreLibListener
from core_lib.error_handling.core_lib_init_exception import CoreLibInitException
from core_lib.jobs.job import Job
from core_lib.jobs.job_scheduler import JobScheduler
from core_lib.observer.observer import Observer
from core_lib.observer.observer_factory import ObserverFactory


class CoreLib(object):

    cache_factory = CacheFactory()
    observer_factory = ObserverFactory()
    scheduler = JobScheduler()

    def __init__(self):
        self._core_lib_started = False
        self._observer = Observer(listener_type=CoreLibListener)
        self.logger = logging.getLogger(__name__)

    def load_jobs(self, config: DictConfig):
        if 'jobs' not in config.core_lib:
            self.logger.info('No CoreLib jobs `{}`'.format(self.__class__.__name__))
            return

        self.logger.info('Loading CoreLib jobs `{}`'.format(self.__class__.__name__))
        for job_config in config.core_lib.jobs:
            if not job_config.initial_delay:
                raise ValueError('job invalid initial_delay config  `{}`'.format(job_config.initial_delay))

            initial_delay = job_config.initial_delay
            if job_config.initial_delay in ['boot', 'startup']:
                initial_delay = '0s'

            try:
                job = instantiate(job_config.handler)
                if not isinstance(job, Job):
                    raise ValueError("processor must be a baseclass of 'BaseProcessor'. Got: {} ".format(job.__class__.__name__))
                if job_config.frequency:
                    CoreLib.scheduler.schedule(initial_delay, job_config.frequency, job)
                else:
                    CoreLib.scheduler.schedule_once(initial_delay, job)
                self.logger.info('job `{}` started with params. initial_delay:`{}`, frequency:`{}`'.format(job.__class__.__name__, job_config.initial_delay, job_config.frequency))
            except BaseException as ex :
                raise ValueError('job initialization failed `{}`'.format(job_config.pretty())) from ex

    def attach_listener(self, core_lib_listener: CoreLibListener):
        self._observer.attach(core_lib_listener)

    def detach_listener(self, conversation_listener: CoreLibListener):
        self._observer.detach(conversation_listener)

    def fire_core_lib_ready(self):
        self._observer.notify(CoreLibListener.CoreLibEventType.CORE_LIB_READY, None)

    def start_core_lib(self):
        self.logger.info('Starting CoreLib `{}`'.format(self.__class__.__name__))
        if self._core_lib_started:
            raise CoreLibInitException('CoreLib already initialized')

        self.fire_core_lib_ready()

        self._core_lib_started = True
