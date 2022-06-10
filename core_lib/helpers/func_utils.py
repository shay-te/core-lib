import inspect
import logging
from abc import ABC, abstractmethod
from string import Formatter

logger = logging.getLogger(__name__)


def get_func_parameter_index_by_name(func, parameter_name: str) -> int:
    parameters = inspect.signature(func).parameters
    if parameter_name not in parameters:
        raise ValueError(
            f'parameter named: `{parameter_name}`. dose not exists in the decorated function. `{func.__name__}`'
        )

    return list(parameters).index(parameter_name)


class Keyable(ABC):
    @abstractmethod
    def key(self) -> str:
        pass


def _get_key_value(key, value):
    if value:
        return value.key() if isinstance(value, Keyable) else value
    return f'!E{key}E!'


class UnseenFormatter(Formatter):
    def get_value(self, key, args, kwargs):
        try:
            if isinstance(key, int) and key < len(args):
                return _get_key_value(key, args[key])
            if isinstance(key, str) and key in kwargs:
                return _get_key_value(key, kwargs[key])
            return f'!M{key}M!'
        except BaseException:
            logger.warning(f'Error while building key. `{key}`', exc_info=True)
            return f'!E{key}E!'


_formatter = UnseenFormatter()


def get_func_parameters_as_dict(func, *args, **kwargs) -> dict:
    parameters = inspect.signature(func).parameters
    parameters_lst = list(parameters)

    result = {}
    for param_index, param in enumerate(parameters_lst):
        if param_index < len(args):
            result[param] = args[param_index]
        elif param in kwargs:
            result[param] = kwargs[param]
        elif param in parameters and parameters[param].default != inspect.Parameter.empty:
            result[param] = parameters[param].default
        else:
            result[param] = None
    return result


def build_function_key(key: str, func, *args, **kwargs) -> str:
    if key:
        new_key = _formatter.format(key, **get_func_parameters_as_dict(func, *args, **kwargs))
    else:
        new_key = func.__qualname__
    return new_key.replace('\n', '').replace('\r', '')
