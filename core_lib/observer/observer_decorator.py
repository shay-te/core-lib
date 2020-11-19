from functools import wraps

from core_lib.core_lib import CoreLib
from core_lib.helpers.func_utils import get_func_parameter_index_by_name, get_func_parameters_as_dict


class Observe(object):

    _factory = None

    def __init__(self, event_key: str,
                 value_param_name: str = None,
                 observer_name: str = None,
                 notify_before: bool = False):
        self.event_key = event_key
        self.value_param_name = value_param_name
        self.observer_name = observer_name
        self.notify_before = notify_before

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def __wrapper(*args, **kwargs):
            if self.value_param_name:
                parameter_index = get_func_parameter_index_by_name(func, self.value_param_name)
                value = args[parameter_index]
            else:
                value = get_func_parameters_as_dict(func, *args, **kwargs)

            observer = CoreLib.observer_registry.get(self.observer_name)
            if self.notify_before:
                observer.notify(self.event_key, value)

            result = func(*args, **kwargs)

            if not self.notify_before:
                observer.notify(self.event_key, value)
            return result

        return __wrapper
