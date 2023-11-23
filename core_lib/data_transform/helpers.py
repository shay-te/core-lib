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


def enums_to_dict(enums: list) -> dict:
    result = {}
    for enum in enums:
        enum_name = camel_to_snake(enum.__name__).lower()
        result[enum_name] = {e.name: e.value for e in enum}
    return result
