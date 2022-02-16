import datetime
import inspect
import logging
from contextlib import suppress
from string import Formatter

logger = logging.getLogger(__name__)


def get_func_parameter_index_by_name(func, parameter_name: str) -> str:
    parameters = inspect.signature(func).parameters
    if parameter_name not in parameters:
        raise ValueError(
            f'parameter named: `{parameter_name}`. dose not exists in the decorated function. `{func.__name__}`'
        )

    return list(parameters).index(parameter_name)


class UnseenFormatter(Formatter):
    def get_value(self, key, args, kwargs):
        try:
            if isinstance(key, int) and key < len(args):
                return args[key]
            if isinstance(key, str) and key in kwargs:
                return kwargs[key]
            return '!M{}M!'.format(key)
        except BaseException:
            logger.warning(f'Error while building key. `{key}`', exc_info=True)
            return '!E{}E!'.format(key)


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
            result[param] = param
    return result


def build_value_by_func_parameters(key: str, func, *args, **kwargs):
    if key:
        new_key = _formatter.format(key, **get_func_parameters_as_dict(func, *args, **kwargs))
    else:
        new_key = func.__qualname__
    return new_key


def get_calling_module(stack_depth: int = 1):
    stack = inspect.stack()
    frame = stack[stack_depth]
    calling_module = None
    with suppress(Exception):
        calling_module = frame[0].f_globals[frame[3]].__module__
    if not calling_module:
        with suppress(Exception):
            calling_module = frame[0].f_locals["self"].__module__
    if not calling_module:
        with suppress(Exception):
            calling_module = frame[0].f_locals['__module__']
    return calling_module


def reset_datetime(date: datetime):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)
