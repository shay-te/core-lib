import logging

logger = logging.getLogger(__name__)


def get_dict_attr(obj: dict, path: str):
    path_list = path.split('.')
    obj_temp = obj
    try:
        for elem in path_list:
            obj_temp = obj_temp[elem]
        return obj_temp
    except KeyError as e:
        logger.error('Key Not Found')


def set_dict_attr(obj: dict, path: str, value) -> dict:
    path_list = path.split('.')
    obj_temp = obj
    for key in path_list[:-1]:
        if obj_temp.get(key, None) is None:
            obj_temp.setdefault(key, {})
        obj_temp = obj_temp[key]
    obj_temp[path_list[-1]] = value
    return obj
