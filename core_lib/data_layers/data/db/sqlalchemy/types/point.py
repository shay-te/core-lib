import re

from sqlalchemy import func
from sqlalchemy.types import UserDefinedType
from geoalchemy2.shape import to_shape


# Match a signed float (with optional decimals / scientific notation).
_FLOAT_PATTERN = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?')


class Point(UserDefinedType):
    def get_col_spec(self):
        return "POINT"

    def bind_expression(self, bindvalue):
        return func.ST_GeomFromText(bindvalue, type_=self)

    def column_expression(self, col):
        return func.ST_AsText(col, type_=self)

    @staticmethod
    def from_point_wkb(point):
        shape = to_shape(point)
        return {'latitude': shape.y, 'longitude': shape.x}

    @staticmethod
    def from_point_str(point_str: str, latitude_first: bool = False):
        # Previously: `point_str.strip('POINT()').replace(' ', ',').split(',')`
        # which chokes on extra whitespace ("POINT(  5  45  )" → empty
        # segments → float('') → ValueError). Use a regex to extract the
        # two numeric components so whitespace and minor formatting variation
        # are tolerated.
        numbers = _FLOAT_PATTERN.findall(point_str)
        if len(numbers) < 2:
            raise ValueError(f'Cannot parse POINT string: {point_str!r}')
        first, second = float(numbers[0]), float(numbers[1])
        if latitude_first:
            return {'latitude': first, 'longitude': second}
        return {'longitude': first, 'latitude': second}

    @staticmethod
    def to_point_str(longitude: float, latitude: float, latitude_first: bool = False):
        if latitude_first:
            return 'POINT({} {})'.format(latitude, longitude)
        else:
            return 'POINT({} {})'.format(longitude, latitude)
