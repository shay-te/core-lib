import datetime
import enum
from collections import Iterable
from typing import Callable, Awaitable

from sqlalchemy import inspect
from sqlalchemy.orm import class_mapper

from core_lib.data_layers.data.db.base import Base


def __transform_value(value):
    if isinstance(value, enum.Enum):
        value = value.value
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value


def __tuple_to_dict(obj):
    result = {}
    for key in obj._fields:
        result[key] = __transform_value(getattr(obj, key))
    return result


def __base_as_dict(obj, found=None):
    if not found:
        found = set()
    result = {}
    mapper = inspect(obj).mapper
    for c in mapper.column_attrs:
        result[c.key] = __transform_value(getattr(obj, c.key))

    for name, relation in mapper.relationships.items():
        if relation not in found:
            found.add(relation)
            try:
                related_obj = getattr(obj, name)
                print(related_obj)
                if related_obj is not None:
                    if isinstance(related_obj, Iterable):
                        result_arr = []
                        for r_obj in related_obj:
                            result_arr.append(__base_as_dict(r_obj, found))
                        result[name] = result_arr
                    else:
                        result[name] = __base_as_dict(related_obj, found)
            except:
                pass # Do nothing here unable to load relationship

        # __base_as_dict

    return result


def __convert_object(value):
    return value


def result_to_dict(return_val, properties_as_dict: bool = True, callback: Callable[[dict], Awaitable[dict]] = None):
    if isinstance(return_val, list) and return_val:
        results = []
        for entity in return_val:
            results.append(result_to_dict(entity, properties_as_dict=properties_as_dict, callback=callback))
        return results

    # Do the actual conversion
    if isinstance(return_val, Base):
        results = __base_as_dict(return_val)
    elif isinstance(return_val, tuple):
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
        def __wrapper(*args, **kwargs):
            return_val = func(*args, **kwargs)
            return result_to_dict(return_val, properties_as_dict=True, callback=self.callback)
        return __wrapper

