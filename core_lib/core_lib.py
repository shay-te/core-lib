import logging

from core_lib.core_lib_listener import CoreLibListener
from core_lib.exceptions.core_lib_init_exception import CoreLibInitException
from core_lib.single_instance import SingleInstance

logger = logging.getLogger(__name__)


class CoreLib(SingleInstance):

    _core_lib_started = False

    def start_core_lib(self):
        if CoreLib._core_lib_started:
            raise CoreLibInitException('CoreLib already initialized')

        for key, instance in SingleInstance._instances.items():
            if isinstance(instance, CoreLibListener):
                try:
                    instance.on_core_lib_ready()
                except BaseException as ex:
                    logger.error("error on on_core_lib_ready event for class `{}`".format(instance))

        CoreLib._core_lib_started = True
