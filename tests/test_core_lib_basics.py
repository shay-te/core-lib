import unittest

from core_lib.core_lib import CoreLib
from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.core_lib_listener import CoreLibListener
from core_lib.data_layers.service.service import Service


class EventsDataAccess(DataAccess, CoreLibListener):

    def __init__(self):
        self.core_lib_ready_data_access_called = False

    def on_core_lib_ready(self):
        self.core_lib_ready_data_access_called = True
        raise ValueError("Error on core lib ready data access event")


class EventsService(Service, CoreLibListener):

    def __init__(self, data_access: EventsDataAccess):
        self.data_access = data_access
        self.core_lib_ready_service_called = False

    def on_core_lib_ready(self):
        self.core_lib_ready_service_called = True
        raise ValueError("Error on core lib ready service event")


class EventsCoreLib(CoreLib, CoreLibListener):

    def __init__(self):
        CoreLib.__init__(self)
        self.core_lib_ready_called = False

        data_access = EventsDataAccess()
        self.service = EventsService(data_access)

        self._data_access = data_access

        self.register_listener(self)
        self.register_listener(self.service)
        self.register_listener(self._data_access)

    @property
    def core_lib_ready_service_called(self):
        return self.service.core_lib_ready_service_called

    @property
    def core_lib_ready_data_access_called(self):
        return self._data_access.core_lib_ready_data_access_called

    def on_core_lib_ready(self):
        self.core_lib_ready_called = True
        raise ValueError("Error on core lib ready event")


class TestCoreLibBasics(unittest.TestCase):

    def test_01_events(self):
        core_lib = EventsCoreLib()
        core_lib.start_core_lib()

        self.assertEqual(core_lib.core_lib_ready_called, True)
        self.assertEqual(core_lib.core_lib_ready_data_access_called, True)
        self.assertEqual(core_lib.core_lib_ready_service_called, True)
