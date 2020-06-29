from functools import wraps

from core_lib.factory.factory import Factory
from core_lib.helpers.func_utils import get_func_parameter_index_by_name, get_func_parameters_as_dict
from core_lib.observer.observer import Observer


class ObserverNotify(object):

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

            if self.notify_before:
                self._get_observer().notify(self.event_key, value)

            result = func(*args, **kwargs)

            if not self.notify_before:
                self._get_observer().notify(self.event_key, value)
            return result

        return __wrapper

    def _get_observer(self):
        if not ObserverNotify._factory:
            raise ValueError("factory was not set to `{}`".format(self.__class__.__name__))

        observer = ObserverNotify._factory.get(self.observer_name)
        if not observer:
            raise ValueError("Observer by name `{}` was not found in factory `{}`".format(self.eveobserver_nament_key, ObserverNotify._factory))

        if not isinstance(observer, Observer):
            raise ValueError("Observer by name `{}` not instance of Observer".format(self.observer_name))

        return observer

    @staticmethod
    def set_factory(factory: Factory):
        ObserverNotify._factory = factory
