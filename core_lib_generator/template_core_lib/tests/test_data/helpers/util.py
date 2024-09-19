import os
import threading
import traceback
import hydra
from dotenv import load_dotenv
from hydra.core.global_hydra import GlobalHydra

from core_lib.core_lib import CoreLib
# template_core_lib_import


class TemplateInstance(object):
    instance = None
    config = None


threadLock = threading.Lock()


def load_config():
    if not TemplateInstance.config:
        path = os.path.join(os.path.dirname(__file__), '..', 'data')
        load_dotenv(dotenv_path=os.path.join(path, '.env'))

        GlobalHydra.instance().clear()
        hydra.initialize(config_path=os.path.join(f'../../../../{core_lib_name}', 'data', 'config'), caller_stack_depth=1)
        TemplateInstance.config = hydra.compose('config.yaml')
    return TemplateInstance.config


def sync_create_start_core_lib() -> TemplateCoreLibClass:
    threadLock.acquire()
    if not TemplateInstance.instance:
        try:
            [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
            [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
            config = load_config()
            TemplateInstance.instance = TemplateCoreLibClass(config)
            TemplateInstance.instance.install(config)
            TemplateInstance.instance.start_core_lib()
        except BaseException as e:
            print(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
            raise e

    # Clear the cache
    for key in CoreLib.cache_registry.registered():
        CoreLib.cache_registry.get(key).flush_all()

    threadLock.release()
    return TemplateInstance.instance
