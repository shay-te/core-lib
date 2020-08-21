import datetime
import enum
from collections import Iterable
from functools import wraps
from typing import Callable, Awaitable

from sqlalchemy import inspect

from core_lib.data_layers.data.db.sqlalchemy.base import Base


def __convert_value(value):
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value


def __name_tuple_to_dict(obj):
    result = {}
    for key in obj._fields:
        result[key] = __convert_value(getattr(obj, key))
    return result


def __tuple_to_dict(obj):
    return [__convert_value(item) for item in obj]


def __base_to_dict(obj, found=None):
    if not found:
        found = set()

    result = {}
    mapper = inspect(obj).mapper
    for c in mapper.column_attrs:
        result[c.key] = __convert_value(getattr(obj, c.key))

    for name, relation in mapper.relationships.items():
        if relation not in found:
            found.add(relation)
            try:
                related_obj = getattr(obj, name)
                if related_obj is not None:
                    if isinstance(related_obj, Iterable):
                        result_arr = []
                        for r_obj in related_obj:
                            result_arr.append(__base_to_dict(r_obj, found))
                        result[name] = result_arr
                    else:
                        result[name] = __base_to_dict(related_obj, found)
            except:
                pass # Do nothing here unable to load relationship

    return result


def result_to_dict(return_val, properties_as_dict: bool = True, callback: Callable[[dict], Awaitable[dict]] = None):
    if isinstance(return_val, list) and return_val:
        results = []
        for entity in return_val:
            results.append(result_to_dict(entity, properties_as_dict=properties_as_dict, callback=callback))
        return results

    # Do the actual conversion
    if isinstance(return_val, Base):
        results = __base_to_dict(return_val)
        # get also fields that was loaded onto the model
        for key, value in return_val.__dict__.items():
            if key not in results and key != '_sa_instance_state':
                results[key] = result_to_dict(value, properties_as_dict=properties_as_dict, callback=callback)

    elif isinstance(return_val, tuple):
        if hasattr(return_val, '_fields') and len(return_val._fields) > 0:
            results = __name_tuple_to_dict(return_val)
        else:
            results = __tuple_to_dict(return_val)
    else:
        results = return_val

    if isinstance(results, dict):
        if properties_as_dict:
            for key, value in results.items():
                if not isinstance(value, (int, float, bool, str)):
                    results[key] = result_to_dict(value, properties_as_dict=properties_as_dict, callback=callback)

    # must be last!
    if callback:
        results = callback(results)

    return results


class ResultToDict(object):

    def __init__(self, callback: Callable[[dict], Awaitable[dict]] = None):
        self.callback = callback

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def __wrapper(*args, **kwargs):
            return_val = func(*args, **kwargs)
            return result_to_dict(return_val, properties_as_dict=True, callback=self.callback)
        return __wrapper
