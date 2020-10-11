from sqlalchemy import func
from sqlalchemy.types import UserDefinedType


class Point(UserDefinedType):

    def get_col_spec(self):
        return "POINT"

    def bind_expression(self, bindvalue):
        return func.ST_GeomFromText(bindvalue, type_=self)

    def column_expression(self, col):
        return func.ST_AsText(col, type_=self)

    @staticmethod
    def from_point_str(point_str: str):
        location_arr = point_str.strip('POINT()').replace(' ', ',').split(',')
        return {
            'latitude': float(location_arr[0]),
            'longitude': float(location_arr[1])
        }

    @staticmethod
    def to_point_str(latitude: float, longitude: float, latitude_first: bool = True):
        if latitude_first:
            return 'POINT({} {})'.format(latitude, longitude)
        else:
            return 'POINT({} {})'.format(longitude, latitude)
