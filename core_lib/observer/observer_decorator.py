from functools import wraps

from core_lib.cache.cache_decorator import Cache
from core_lib.factory.factory import Factory
from core_lib.helpers.func_utils import get_parameter_index_by_name
from core_lib.observer.observer import Observer


class ObserverNotify(object):

    _factory = None

    def __init__(self, event_key: str,
                 value_param_name: str = None,
                 observer_name: str = None):
        self.event_key = event_key
        self.value_param_name = value_param_name
        self.observer_name = observer_name

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def __wrapper(*args, **kwargs):
            value = None
            if self.value_param_name:
                parameter_index = get_parameter_index_by_name(func, self.value_param_name)
                value = args[parameter_index]

            self._get_observer().notify(self.event_key, value)
            return func(*args, **kwargs)

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
