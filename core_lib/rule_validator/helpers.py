from core_lib.data_layers.data.db.sqlalchemy.types.point import Point


def location_convertor(location: dict):
    if location:
        latitude = location.get('lat') or location.get('latitude')
        longitude = location.get('lng') or location.get('longitude')
        return Point.to_point_str(longitude, latitude)
    return None


def location_validate(point: str):
    if point:
        location = Point.from_point_str(point)
        latitude = location.get('lat') or location.get('latitude')
        longitude = location.get('lng') or location.get('longitude')
        return True if -90 <= latitude <= 90 and -180 <= longitude <= 180 else False
    return True
