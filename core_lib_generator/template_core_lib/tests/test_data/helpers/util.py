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
        project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

        GlobalHydra.instance().clear()
        # tests/test_data/test_config/config.yaml, relative to this file
        hydra.initialize(config_path=os.path.join('..', 'test_config'), caller_stack_depth=1, version_base=None)
        TemplateInstance.config = hydra.compose('config.yaml')
    return TemplateInstance.config


def sync_create_start_core_lib() -> TemplateCoreLibClass:
    threadLock.acquire()
    try:
        if not TemplateInstance.instance:
            [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
            [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
            TemplateInstance.instance = TemplateCoreLibClass(load_config())
            TemplateInstance.instance.start_core_lib()

        # Clear the cache
        for key in CoreLib.cache_registry.registered():
            CoreLib.cache_registry.get(key).flush_all()
    except BaseException as e:
        print(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        raise e
    finally:
        threadLock.release()
    return TemplateInstance.instance
