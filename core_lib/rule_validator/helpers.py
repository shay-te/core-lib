import datetime

from core_lib.data_layers.data.db.sqlalchemy.types.point import Point


def convert_location(location: dict):
    if location:
        latitude = location.get('lat') or location.get('latitude')
        longitude = location.get('lng') or location.get('longitude')
        return Point.to_point_str(longitude, latitude)
    return None


def validate_location(point: str):
    if point:
        location = Point.from_point_str(point)
        latitude = location.get('lat') or location.get('latitude')
        longitude = location.get('lng') or location.get('longitude')
        return True if -90 <= latitude <= 90 and -180 <= longitude <= 180 else False
    return True


def convert_datetime(value):
    if value:
        if isinstance(value, (int, float)):
            return datetime.datetime.fromtimestamp(value)
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime(year=value.year, month=value.month, day=value.day)
        else:
            return value
    return None
