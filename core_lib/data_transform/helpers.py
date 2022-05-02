def get_dict_attr(obj: dict, path: str):
    path_list = path.split('.')
    obj_temp = obj
    try:
        for elem in path_list:
            obj_temp = obj_temp[elem]
        print(obj_temp)
    except KeyError:
        print('Not found')


def set_dict_attr(obj: dict, path: str, value):
    path_list = path.split('.')
    path_len = len(path_list)
    updated_obj = obj
    if path_len == 1:
        updated_obj[path_list[0]] = value
    elif path_len == 2:
        updated_obj = _update(obj, path_list, value)
    else:
        updated_obj = _update(obj, path_list, value)
        for index in range(1, path_len):
            updated_path_list = path_list[:-index]
            if len(updated_path_list) >= 2:
                updated_obj = _update(obj, updated_path_list, updated_obj)
    print(updated_obj)


def _update(obj: dict, path: list, new_value) -> dict:
    for key, value in obj.items():
        if isinstance(value, dict):
            if key == path[-2]:
                value.setdefault(path[-1], new_value)
                return {key: value}
            return _update(value, path, new_value)


if __name__ == '__main__':
    print(set_dict_attr({'person': {'name': 'aaad', 'age': 131, 'object': {'person2': {'name': 'name', 'age': 478}}}},
                  'person.object.person2.name', 'adas'))
