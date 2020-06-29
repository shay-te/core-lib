import inspect


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


