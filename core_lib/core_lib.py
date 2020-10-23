import logging

from hydra.utils import instantiate
from omegaconf import DictConfig

from core_lib.cache.cache_factory import CacheFactory
from core_lib.core_lib_listener import CoreLibListener
from core_lib.error_handling.core_lib_init_exception import CoreLibInitException
from core_lib.helpers.config_instances import from_config_dict, from_config_list
from core_lib.jobs.job import Job
from core_lib.jobs.job_scheduler import JobScheduler
from core_lib.observer.observer import Observer
from core_lib.observer.observer_factory import ObserverFactory

logger = logging.getLogger(__name__)


class CoreLib(object):

    cache_factory = CacheFactory()
    observer_factory = ObserverFactory()
    scheduler = JobScheduler()

    def __init__(self):
        self._core_lib_started = False
        self._observer = Observer(listener_type=CoreLibListener)

    def load_jobs(self, config: DictConfig):
        if 'jobs' not in config.core_lib:
            logger.info('No CoreLib jobs `{}`'.format(self.__class__.__qualname__))
            return

        logger.info('Loading CoreLib jobs `{}`'.format(self.__class__.__qualname__))

        for job, job_config in from_config_list(config.core_lib.jobs,
                                                             Job,
                                                             class_config_path='handler',
                                                             class_config_path_error=True):
            if not job_config.initial_delay:
                raise ValueError('job invalid initial_delay config  `{}`'.format(job_config.initial_delay))

            initial_delay = job_config.initial_delay
            if job_config.initial_delay in ['boot', 'startup']:
                initial_delay = '0s'

            job.set_core_lib(self)
            if job_config.frequency:
                CoreLib.scheduler.schedule(initial_delay, job_config.frequency, job)
            else:
                CoreLib.scheduler.schedule_once(initial_delay, job)

            if isinstance(job, CoreLibListener):
                logger.debug('job `{}`, is instance of `{}`, attach as core_lib listener'.format(job.__class__.__qualname__, CoreLibListener.__qualname__))
                self.attach_listener(job)
            logger.info('job `{}` started with params. initial_delay:`{}`, frequency:`{}`'.format(job.__class__.__qualname__, job_config.initial_delay, job_config.frequency))

    def attach_listener(self, core_lib_listener: CoreLibListener):
        self._observer.attach(core_lib_listener)

    def detach_listener(self, conversation_listener: CoreLibListener):
        self._observer.detach(conversation_listener)

    def fire_core_lib_ready(self):
        self._observer.notify(CoreLibListener.CoreLibEventType.CORE_LIB_READY, None)

    def fire_core_lib_destroy(self):
        if hasattr(self, '_observer'):
            self._observer.notify(CoreLibListener.CoreLibEventType.CORE_LIB_DESTROY, None)

    def start_core_lib(self):
        logger.info('Starting CoreLib `{}`'.format(self.__class__.__name__))
        if self._core_lib_started:
            raise CoreLibInitException('CoreLib already initialized')

        self.fire_core_lib_ready()
        self._core_lib_started = True

    def __del__(self):
        self.fire_core_lib_destroy()
