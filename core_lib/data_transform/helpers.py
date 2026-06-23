import enum as _enum


def get_dict_attr(obj: dict, path: str, default=None):
    """
    Look up a nested value using a dotted path in a dictionary.
    
    Traverses the dictionary by splitting the path on `.` and indexing into each successive level. Returns the value at the final path component, or `default` if any key is missing, a non-subscriptable value is encountered during traversal, or a numeric index is out of range.
    
    Parameters:
    	obj (dict): Dictionary to traverse
    	path (str): Dotted path (e.g. "foo.bar.baz")
    	default: Value to return if the path cannot be fully resolved
    
    Returns:
    	The value at the specified path, or `default` if resolution fails
    """
    path_list = path.split('.')
    obj_temp = obj
    try:
        for elem in path_list:
            obj_temp = obj_temp[elem]
        return obj_temp
    # KeyError: missing dict key; TypeError: descended into a
    # non-subscriptable value (None, scalar); IndexError: numeric index
    # past end of list.
    except (KeyError, TypeError, IndexError):
        return default


def set_dict_attr(obj: dict, path: str, value) -> dict:
    """
    Set a value at a dotted path within a nested dictionary, creating intermediate dictionaries as needed.
    
    If an intermediate position is not a dictionary, it is replaced with an empty dictionary.
    
    Returns:
        dict: The modified dictionary (same object as obj).
    """
    path_list = path.split('.')
    obj_temp = obj
    for key in path_list[:-1]:
        existing = obj_temp.get(key)
        if not isinstance(existing, dict):
            obj_temp[key] = {}
        obj_temp = obj_temp[key]
    obj_temp[path_list[-1]] = value
    return obj


def enum_to_dict(enum_cls: _enum.EnumMeta) -> dict:
    """
    Create a dictionary mapping Enum member names to their values.
    
    Returns:
        dict: Dictionary with member names as keys and member values as values
    """
    return {name: member.value for name, member in enum_cls.__members__.items()}
