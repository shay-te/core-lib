import logging

from omegaconf import DictConfig

from core_lib.cache.cache_registry import CacheRegistry
from core_lib.connection.connection_factory_registry import ConnectionFactoryRegistry
from core_lib.core_lib_listener import CoreLibListener
from core_lib.error_handling.core_lib_init_exception import CoreLibInitException
from core_lib.helpers.config_instances import instantiate_config_group_generator_dict
from core_lib.jobs.job import Job
from core_lib.jobs.job_scheduler import JobScheduler
from core_lib.middleware.middleware_chain import MiddlewareChain
from core_lib.observer.observer import Observer
from core_lib.observer.observer_registry import ObserverRegistry

logger = logging.getLogger(__name__)


class CoreLib(object):
    cache_registry = CacheRegistry()
    observer_registry = ObserverRegistry()
    connection_factory_registry = ConnectionFactoryRegistry()
    handle_exception_middleware = MiddlewareChain()
    scheduler = JobScheduler()

    def __init__(self):
        """Initialize a CoreLib instance."""
        self._core_lib_started = False
        self._observer = Observer(listener_type=CoreLibListener)

    def load_jobs(self, config: DictConfig, job_to_data_handler: dict = None):
        # Resolve mutable default internally — avoids the Python gotcha
        # where every caller shares the same default dict instance.
        """
        Load and schedule jobs from a configuration object.
        
        Jobs are instantiated from the configuration, optionally assigned data handlers,
        and scheduled for execution based on their initial_delay and frequency settings.
        If a job implements CoreLibListener, it is automatically attached as a core library
        event listener.
        
        Parameters:
            config (DictConfig): Configuration containing job definitions.
            job_to_data_handler (dict): Optional mapping of job names to their data handlers.
        
        Raises:
            ValueError: If a job's initial_delay configuration is missing or invalid.
        """
        if job_to_data_handler is None:
            job_to_data_handler = {}
        logger.info(f'Loading CoreLib jobs `{self.__class__.__qualname__}`')

        for job_name, job, job_config in instantiate_config_group_generator_dict(
            config, Job, class_config_base_path='handler', raise_class_config_base_path_error=True
        ):
            initial_delay = job_config.get('initial_delay')
            frequency = job_config.get('frequency')

            if not initial_delay:
                raise ValueError(f'job invalid initial_delay config `{job_config.initial_delay}`')

            if initial_delay in ['boot', 'startup']:
                initial_delay = '0s'

            if job_name in job_to_data_handler:
                job.set_data_handler(job_to_data_handler.get(job_name))

            if frequency:
                CoreLib.scheduler.schedule(initial_delay, frequency, job)
            else:
                CoreLib.scheduler.schedule_once(initial_delay, job)

            if isinstance(job, CoreLibListener):
                logger.debug(
                    f'job `{job.__class__.__qualname__}`, is instance of `{CoreLibListener.__qualname__}`, '
                    f'attach as core_lib listener'
                )
                self.attach_listener(job)
            logger.info(
                f'job `{job.__class__.__qualname__}` started with params. '
                f'initial_delay:`{initial_delay}`, frequency:`{frequency}`'
            )

    def attach_listener(self, core_lib_listener: CoreLibListener):
        self._observer.attach(core_lib_listener)

    def detach_listener(self, core_lib_listener: CoreLibListener):
        self._observer.detach(core_lib_listener)

    def fire_core_lib_ready(self):
        """
        Notifies all listeners that CoreLib is ready.
        """
        self._observer.notify(CoreLibListener.CoreLibEventType.CORE_LIB_READY, None)

    def fire_core_lib_destroy(self):
        # Idempotent: fires the destroy event at most once. `__del__` is an
        # unreliable trigger in Python (may fire during interpreter shutdown
        # when state is already partially torn down), so guard everything.
        """
        Notify all attached listeners that CoreLib is being destroyed.
        
        This method is idempotent and safe to call multiple times. It suppresses any exceptions during notification to prevent errors during interpreter shutdown or destructor execution.
        """
        if getattr(self, '_destroyed', False):
            return
        if hasattr(self, '_observer'):
            try:
                self._observer.notify(CoreLibListener.CoreLibEventType.CORE_LIB_DESTROY, None)
            except Exception:
                # Swallow errors here — we're typically inside __del__ and
                # raising would print "Exception ignored in:" warnings.
                pass
        self._destroyed = True

    def start_core_lib(self):
        """
        Initialize CoreLib and notify all listeners that it is ready.
        
        Raises:
            CoreLibInitException: If CoreLib has already been initialized.
        """
        logger.info('Starting CoreLib `{}`'.format(self.__class__.__name__))
        if self._core_lib_started:
            raise CoreLibInitException('CoreLib already initialized')

        self.fire_core_lib_ready()
        self._core_lib_started = True

    def __del__(self):
        # fire_core_lib_destroy is idempotent and swallows its own listener
        # exceptions, so this call is safe even during interpreter shutdown.
        """
        Ensure cleanup of CoreLib resources when the object is garbage collected.
        
        This destructor is safe to call even during interpreter shutdown, as fire_core_lib_destroy is idempotent and handles exceptions internally.
        """
        self.fire_core_lib_destroy()
