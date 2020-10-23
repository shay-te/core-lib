import inspect
import logging
from string import Formatter

logger = logging.getLogger(__name__)


def get_func_parameter_index_by_name(func, parameter_name: str) -> str:
    parameters = inspect.signature(func).parameters
    if parameter_name not in parameters:
        raise ValueError("parameter named: `{}`. dose not exists in the decorated function. `{}` ".format(parameter_name, func.__name__))

    return list(parameters).index(parameter_name)


def get_func_parameters_as_dict(func, *args, **kwargs) -> dict:
    parameters = inspect.signature(func).parameters
    parameters_lst = list(parameters)
    result = {}
    for key, val in parameters.items():
        param_index = parameters_lst.index(key)
        if param_index < len(args):
            result[key] = args[param_index]
        elif key in kwargs:
            result[key] = kwargs[key]
    return result


class UnseenFormatter(Formatter):

    def get_value(self, key, args, kwargs):
        try:
            if isinstance(key, int) and key < len(args):
                return args[key]
            if isinstance(key, str) and key in kwargs:
                return kwargs[key]
            return '!M{}M!'.format(key)
        except BaseException as ex:
            logger.warning('Error while building key. `{}`'.format(key), exc_info=True)
            return '!E{}E!'.format(key)


_formatter = UnseenFormatter()


def build_value_by_func_parameters(key: str, func, *args, **kwargs):
    if key:
        params = [k[0] for k in inspect.signature(func).parameters.items()]
        format_params = {**{p: p for p in params}, **kwargs}

        for index, arg in enumerate(args):
            if params[index] != 'self':
                param_name = params[index]
                format_params[param_name] = args[index]

        new_key = _formatter.format(key, **format_params)
    else:
        new_key = func.__qualname__

    return new_key
