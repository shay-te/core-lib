import inspect


def get_parameter_index_by_name(func, parameter_name: str) -> str:
    parameters = inspect.signature(func).parameters
    if parameter_name not in parameters:
        raise ValueError("parameter named: `{}`. dose not exists in the decorated function. `{}` ".format(parameter_name, func.__name__))

    return list(parameters).index(parameter_name)




