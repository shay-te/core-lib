import datetime
from typing import Optional

from core_lib.data_layers.data.db.sqlalchemy.types.point import Point


def convert_location(location: Optional[dict]):
    """
    Convert a location dictionary to a point string representation.
    
    Parameters:
        location: A dictionary with latitude ('lat' or 'latitude') and longitude ('lng' or 'longitude').
    
    Returns:
        A point string representation of the location, or None if location is not provided.
    """
    if location:
        latitude = location.get('lat') or location.get('latitude')
        longitude = location.get('lng') or location.get('longitude')
        return Point.to_point_str(longitude, latitude)
    return None


def validate_location(point: Optional[str]):
    """
    Validates that a point string contains valid geographic coordinates.
    
    A point is considered valid if its latitude is within -90 to 90 degrees and longitude is within -180 to 180 degrees. If no point is provided, validation passes.
    
    Returns:
    	`True` if the point contains valid geographic coordinates or if no point is provided, `false` otherwise.
    """
    if point:
        location = Point.from_point_str(point)
        latitude = location.get('lat') or location.get('latitude')
        longitude = location.get('lng') or location.get('longitude')
        return -90 <= latitude <= 90 and -180 <= longitude <= 180
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
