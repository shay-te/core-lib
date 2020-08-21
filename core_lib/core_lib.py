import logging
from typing import List

from core_lib.cache.cache_factory import CacheFactory
from core_lib.core_lib_listener import CoreLibListener
from core_lib.error_handling.core_lib_init_exception import CoreLibInitException
from core_lib.observer.observer_factory import ObserverFactory

logger = logging.getLogger(__name__)


class CoreLib(object):

    cache_factory = CacheFactory()
    observer_factory = ObserverFactory()

    def __init__(self):
        self._core_lib_started = False
        self._observers: List[CoreLibListener] = []

    def register_listener(self, core_lib_listener: CoreLibListener):
        self._observers.append(core_lib_listener)

    def unregister_listener(self, conversation_listener: CoreLibListener):
        self._observers.remove(conversation_listener)

    def fire_core_lib_ready(self):
        for observer in self._observers:
            try:
                observer.on_core_lib_ready()
            except BaseException as ex:
                logger.error("error on file on_core_lib_ready event for observer `{}`".format(observer), exc_info=True)

    def start_core_lib(self):
        if self._core_lib_started:
            raise CoreLibInitException('CoreLib already initialized')

        self.fire_core_lib_ready()

        self._core_lib_started = True
