def get_dict_attr(obj: dict, path: str):
    path_list = path.split('.')
    obj_ptr = obj
    try:
        for elem in path_list:
            obj_ptr = obj_ptr[elem]
        print(obj_ptr)
    except KeyError:
        print('Not found')


def set_dict_attr(obj: dict, path: str, value):
    path_list = path.split('.')
    obj_ptr = obj
    for elem in path_list:
        if elem == path_list[-1]:
            print(elem)
            obj_ptr[elem] = value
    print(obj_ptr)


if __name__ == '__main__':
    set_dict_attr({'person': {'name': 'aaad', 'age': 131, 'object': {'person': {'name': 'aaad', 'age': 131}}}},
                  'person.object.salary', 20000)
