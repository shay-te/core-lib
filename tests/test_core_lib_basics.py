import os
import subprocess
import sys
import textwrap
import threading
import unittest
from time import sleep

from omegaconf import OmegaConf

from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.core_lib_listener import CoreLibListener
from core_lib.data_layers.service.service import Service
from core_lib.error_handling.core_lib_init_exception import CoreLibInitException
from core_lib.jobs.job import Job
from core_lib.observer.observer import Observer
from core_lib.observer.observer_listener import ObserverListener


class EventsDataAccess(DataAccess, CoreLibListener):
    def __init__(self):
        self.core_lib_ready_data_access_called = False

    def on_core_lib_ready(self):
        self.core_lib_ready_data_access_called = True
        # raise ValueError("Error on core lib ready data access event")

    def on_core_lib_destroy(self):
        pass


class EventsService(Service, CoreLibListener):
    def __init__(self, data_access: EventsDataAccess):
        self.data_access = data_access
        self.core_lib_ready_service_called = False

    def on_core_lib_ready(self):
        self.core_lib_ready_service_called = True
        # raise ValueError("Error on core lib ready service event")

    def on_core_lib_destroy(self):
        pass


class EventsCoreLib(CoreLib, CoreLibListener):
    def __init__(self):
        CoreLib.__init__(self)
        self.core_lib_ready_called = False

        data_access = EventsDataAccess()
        self.service = EventsService(data_access)

        self._data_access = data_access

        self.attach_listener(self)
        self.attach_listener(self.service)
        self.attach_listener(self._data_access)

    @property
    def core_lib_ready_service_called(self):
        return self.service.core_lib_ready_service_called

    @property
    def core_lib_ready_data_access_called(self):
        return self._data_access.core_lib_ready_data_access_called

    def on_core_lib_ready(self):
        self.core_lib_ready_called = True
        # raise ValueError("Error on core lib ready event")

    def on_core_lib_destroy(self):
        self.core_lib_ready_called = False


class OtherObserverListener(ObserverListener):
    def update(self, key: str, value):
        pass


class Listener(CoreLibListener):
    state = 'idle'

    def on_core_lib_ready(self):
        # Do some task here
        self.state = 'on_core_lib_ready'

    def on_core_lib_destroy(self):
        # Cleanups here
        self.state = 'on_core_lib_destroy'


class CountingListener(CoreLibListener):
    def __init__(self):
        self.ready_count = 0

    def on_core_lib_ready(self):
        self.ready_count = self.ready_count + 1

    def on_core_lib_destroy(self):
        pass


class StartupJob(Job):
    instances = []

    def __init__(self):
        self.runs = 0
        self.ran = threading.Event()
        StartupJob.instances.append(self)

    def initialized(self, data_handler):
        pass

    def run(self):
        self.runs = self.runs + 1
        self.ran.set()


class BootJob(StartupJob):
    # A class of its own: load_jobs schedules without parallel runs, so two jobs of ONE class that fire at the same
    # moment would run only once.
    pass


class ListenerJob(Job, CoreLibListener):
    instances = []

    def __init__(self):
        self.runs = 0
        self.heard_core_lib_ready = False
        ListenerJob.instances.append(self)

    def initialized(self, data_handler):
        pass

    def run(self):
        self.runs = self.runs + 1

    def on_core_lib_ready(self):
        self.heard_core_lib_ready = True

    def on_core_lib_destroy(self):
        pass


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A CoreLib whose own constructor fails before it calls CoreLib.__init__ is still garbage collected, which runs
# CoreLib.__del__ on an object that never got an observer.
FAILED_CONSTRUCTOR_SCRIPT = textwrap.dedent('''
    import gc
    from core_lib.core_lib import CoreLib

    class AcmeCoreLib(CoreLib):
        def __init__(self, conf):
            if not conf:
                raise ValueError('acme config is missing')
            super().__init__()

    try:
        AcmeCoreLib(None)
    except ValueError as error:
        print(error)
    gc.collect()
''')


def job_config(initial_delay, job_class, frequency=None) -> dict:
    config = {'initial_delay': initial_delay, 'handler': {'_target_': f'{__name__}.{job_class.__qualname__}'}}
    if frequency:
        config['frequency'] = frequency
    return config


class TestCoreLibBasics(unittest.TestCase):
    listener = Listener()

    def setUp(self):
        StartupJob.instances = []
        ListenerJob.instances = []

    def tearDown(self):
        for job in StartupJob.instances + ListenerJob.instances:
            CoreLib.scheduler.stop(job)

    def test_01_events(self):
        core_lib = EventsCoreLib()
        self.assertEqual(self.listener.state, 'idle')
        core_lib.attach_listener(self.listener)
        core_lib.start_core_lib()
        self.assertEqual(self.listener.state, 'on_core_lib_ready')
        self.assertRaises(AssertionError, core_lib.attach_listener, 'ss')
        self.assertRaises(AssertionError, core_lib.attach_listener, OtherObserverListener())

        self.assertEqual(core_lib.core_lib_ready_called, True)
        self.assertEqual(core_lib.core_lib_ready_data_access_called, True)
        self.assertEqual(core_lib.core_lib_ready_service_called, True)

    def test_core_lib_registries(self):
        CoreLib.cache_registry.register('test_cache_key', CacheHandlerRam())
        self.assertTrue('test_cache_key' in CoreLib.cache_registry.registered())
        [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
        self.assertFalse('test_cache_key' in CoreLib.cache_registry.registered())

        test_observer = Observer(Listener())
        CoreLib.observer_registry.register('test_observer_key', test_observer)
        self.assertTrue('test_observer_key' in CoreLib.observer_registry.registered())
        [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
        self.assertFalse('test_observer_key' in CoreLib.observer_registry.registered())

    def test_startup_and_boot_jobs_run_once_right_away(self):
        core_lib = CoreLib()

        core_lib.load_jobs(OmegaConf.create({
            'acme_startup': job_config('startup', StartupJob),
            'acme_boot': job_config('boot', BootJob),
        }))

        self.assertEqual(2, len(StartupJob.instances))
        for job in StartupJob.instances:
            self.assertTrue(job.ran.wait(5))
        sleep(0.5)  # a job with no frequency is not run again
        self.assertEqual([1, 1], [job.runs for job in StartupJob.instances])

    def test_load_jobs_refuses_an_empty_initial_delay(self):
        core_lib = CoreLib()
        for empty_initial_delay in (None, ''):
            with self.assertRaisesRegex(ValueError, 'job invalid initial_delay config'):
                core_lib.load_jobs(OmegaConf.create({'acme_job': job_config(empty_initial_delay, StartupJob)}))

    def test_load_jobs_refuses_a_job_without_initial_delay(self):
        core_lib = CoreLib()
        for struct_mode in (False, True):  # a Hydra-composed config is in struct mode
            config = OmegaConf.create({'acme_job': {'handler': job_config('1h', StartupJob)['handler']}})
            OmegaConf.set_struct(config, struct_mode)

            with self.assertRaisesRegex(ValueError, 'job invalid initial_delay config `None`'):
                core_lib.load_jobs(config)

    def test_job_that_is_a_core_lib_listener_hears_core_lib_ready(self):
        core_lib = CoreLib()
        core_lib.load_jobs(OmegaConf.create({'acme_listener_job': job_config('1h', ListenerJob, frequency='1h')}))
        job = ListenerJob.instances[0]
        self.assertFalse(job.heard_core_lib_ready)

        core_lib.start_core_lib()

        self.assertTrue(job.heard_core_lib_ready)
        self.assertEqual(0, job.runs)  # its first run is an hour away

    def test_detached_listener_does_not_hear_core_lib_ready(self):
        core_lib = CoreLib()
        listener = CountingListener()
        core_lib.attach_listener(listener)

        core_lib.detach_listener(listener)
        core_lib.start_core_lib()

        self.assertEqual(0, listener.ready_count)

    def test_start_core_lib_twice_raises_and_fires_ready_once(self):
        core_lib = CoreLib()
        listener = CountingListener()
        core_lib.attach_listener(listener)
        core_lib.start_core_lib()

        with self.assertRaisesRegex(CoreLibInitException, 'CoreLib already initialized'):
            core_lib.start_core_lib()

        self.assertEqual(1, listener.ready_count)

    def test_listener_ignores_an_event_it_does_not_know(self):
        listener = Listener()

        listener.update('ACME_EVENT', None)
        listener.update('CORE_LIB_READY', None)  # the event's name as a string is not the event

        self.assertEqual('idle', listener.state)

    def test_core_lib_whose_constructor_failed_is_collected_without_an_error(self):
        environment = dict(os.environ, PYTHONPATH=REPO_ROOT, PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run(
            [sys.executable, '-c', FAILED_CONSTRUCTOR_SCRIPT],
            cwd=REPO_ROOT, env=environment, capture_output=True, text=True, timeout=60,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('acme config is missing', result.stdout.strip())
        self.assertNotIn('Exception ignored', result.stderr)
        self.assertNotIn('AttributeError', result.stderr)
