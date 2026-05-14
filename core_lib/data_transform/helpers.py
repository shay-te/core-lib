import enum as _enum


def get_dict_attr(obj: dict, path: str, default=None):
    """Look up a dotted path in a nested dict-like object, returning
    ``default`` if the path can't be resolved.

    Previously only ``KeyError`` was caught, so paths that descended through
    a non-dict (e.g. None, a scalar, a list) propagated ``TypeError``
    instead of falling back to ``default``.
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
    """Set ``value`` at a dotted path inside a nested dict, creating
    intermediate dicts as needed.

    If an intermediate position exists but is NOT a dict (e.g. it's a
    scalar / list), it is replaced with a fresh dict. The previous
    implementation crashed with ``TypeError: ... does not support item
    assignment`` in that case.
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
    """Return ``{member_name: member_value}`` for an Enum class."""
    return {name: member.value for name, member in enum_cls.__members__.items()}
