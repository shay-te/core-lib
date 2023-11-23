import enum
from core_lib.helpers.string import camel_to_snake


def get_dict_attr(obj: dict, path: str, default=None):
    path_list = path.split('.')
    obj_temp = obj
    try:
        for elem in path_list:
            obj_temp = obj_temp[elem]
        return obj_temp
    except KeyError as e:
        return default


def set_dict_attr(obj: dict, path: str, value) -> dict:
    path_list = path.split('.')
    obj_temp = obj
    for key in path_list[:-1]:
        if obj_temp.get(key, None) is None:
            obj_temp.setdefault(key, {})
        obj_temp = obj_temp[key]
    obj_temp[path_list[-1]] = value
    return obj


def enum_to_dict(enum: enum) -> dict:
    result = {}
    for name, enumItem in enum.__members__.items():
        result[name] = enumItem.value
    return  result
