from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.data_layers.data_access.data_access_listener import DataAccessListener
from core_lib.exceptions.core_lib_init_exception import CoreLibInitException
from core_lib.single_instance import SingleInstance


class CoreLib(SingleInstance):
    core_lib_started = False

    def start_core_lib(self):
        if CoreLib.core_lib_started:
            raise CoreLibInitException('CoreLib already initialized')

        for instance in DataAccess._DataAccess__instances:
            if isinstance(instance, DataAccessListener):
                instance.on_core_lib_ready()

        DataAccess._DataAccess__instances = None
        CoreLib.core_lib_started = True
