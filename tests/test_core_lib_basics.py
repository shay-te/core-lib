import unittest
from time import sleep

from core_lib.core_lib import CoreLib
from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.core_lib_listener import CoreLibListener
from core_lib.data_layers.service.service import Service
from core_lib.observer.observer_listener import ObserverListener

state = ''


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


class TestCoreLibBasics(unittest.TestCase):
    listener = Listener()

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
