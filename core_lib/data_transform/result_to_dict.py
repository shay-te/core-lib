import datetime
import enum
import json
from collections.abc import Iterable

from decimal import Decimal
from functools import wraps
from typing import Callable, Awaitable

from sqlalchemy import inspect

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from sqlalchemy.engine.row import Row

# Values from optional backends are converted only when that backend is installed.
try:
    from geoalchemy2 import WKBElement, WKTElement  # the [geo] extra
    from geoalchemy2.shape import to_shape
    from shapely.geometry import mapping
    # What a Geometry column holds: WKB once read from the database, WKT when assigned in code and not yet re-read.
    _GEOMETRY_TYPES = (WKBElement, WKTElement)
except ImportError:
    _GEOMETRY_TYPES = ()

_cursor_types = []
try:
    import pymongo  # the [mongodb] extra
    _cursor_types.append(pymongo.cursor.Cursor)
except ImportError:
    pass  # no MongoDB support installed
try:
    import mongomock  # the [test] extra: an in-memory MongoDB
    _cursor_types.append(mongomock.collection.Cursor)
except ImportError:
    pass  # no in-memory MongoDB installed
_MONGO_CURSOR_TYPES = tuple(_cursor_types)


def __geometry_to_dict(value) -> dict:
    shape = to_shape(value)
    if shape.geom_type == 'Point':
        return {'latitude': shape.y, 'longitude': shape.x}
    # Any other shape as GeoJSON; the JSON round-trip turns shapely's coordinate tuples into lists.
    return json.loads(json.dumps(mapping(shape)))


def __convert_value(value):
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, datetime.datetime):
        return value.timestamp()
    if isinstance(value, datetime.date):
        return datetime.datetime(year=value.year, month=value.month, day=value.day).timestamp()
    if isinstance(value, _GEOMETRY_TYPES):
        return __geometry_to_dict(value)
    if isinstance(value, Decimal):
        return float(value)
    return value


def __name_tuple_to_dict(obj) -> dict:
    result = {}
    for key in obj._fields:
        result[str(key)] = __convert_value(getattr(obj, key))
    return result


def __tuple_to_dict(obj) -> tuple:
    return tuple(__convert_value(item) for item in obj)


def __dict_to_dict(collect) -> dict:
    result = {}
    for key, value in dict(collect).items():
        result[str(key)] = __convert_value(value)
    return result


def __pymongo_to_dict(raw_data) -> list:
    return [entry for entry in raw_data]


def __base_to_dict(obj, found=None) -> dict:
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
            except (ValueError, Exception):
                pass  # Do nothing here unable to load relationship

    return result


def result_to_dict(return_val, properties_as_dict: bool = True, callback: Callable[[dict], Awaitable[dict]] = None):
    if isinstance(return_val, list) and return_val:
        results = []
        for entity in return_val:
            results.append(result_to_dict(entity, properties_as_dict=properties_as_dict, callback=callback))
        return results

    elif isinstance(return_val, dict) and return_val:
        results = __dict_to_dict(return_val)

    elif isinstance(return_val, tuple):
        if hasattr(return_val, '_fields') and len(return_val._fields) > 0:
            results = __name_tuple_to_dict(return_val)
        else:
            results = __tuple_to_dict(return_val)

    # Do the actual conversion
    elif isinstance(return_val, Base):
        results = __base_to_dict(return_val)
        # get also fields that was loaded onto the model
        for key, value in return_val.__dict__.items():
            if key not in results and key != '_sa_instance_state':
                results[key] = result_to_dict(
                    __convert_value(value), properties_as_dict=properties_as_dict, callback=callback
                )

    elif isinstance(return_val, Row):
        # SQLAlchemy 2.0 Row iterates values, not key/value pairs, so dict(row)
        # raises. `_mapping` gives the key/value view on both 1.4 and 2.0.
        results = __dict_to_dict(return_val._mapping)
    else:
        results = return_val

    if isinstance(return_val, _MONGO_CURSOR_TYPES):
        results = __pymongo_to_dict(return_val)

    if isinstance(results, dict):
        if properties_as_dict:
            for key, value in results.items():
                if not isinstance(value, (int, float, bool, str)):
                    results[key] = result_to_dict(value, properties_as_dict=properties_as_dict, callback=callback)

    # must be last!
    if callback:
        results = callback(results) or results

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
