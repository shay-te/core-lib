import unittest

from core_lib.data_layers.data.db.sqlalchemy.types.point import Point


class TestPoint(unittest.TestCase):
    def test_get_col_spec(self):
        self.assertEqual(Point().get_col_spec(), 'POINT')

    def test_to_point_str_default(self):
        self.assertEqual(Point.to_point_str(1.5, 2.5), 'POINT(1.5 2.5)')

    def test_to_point_str_latitude_first(self):
        self.assertEqual(Point.to_point_str(1.5, 2.5, latitude_first=True), 'POINT(2.5 1.5)')

    def test_from_point_str_default(self):
        result = Point.from_point_str('POINT(1.5 2.5)')
        self.assertEqual(result, {'longitude': 1.5, 'latitude': 2.5})

    def test_from_point_str_latitude_first(self):
        result = Point.from_point_str('POINT(1.5 2.5)', latitude_first=True)
        self.assertEqual(result, {'latitude': 1.5, 'longitude': 2.5})

    def test_round_trip(self):
        lon, lat = 10.123456, 20.654321
        point_str = Point.to_point_str(lon, lat)
        result = Point.from_point_str(point_str)
        self.assertAlmostEqual(result['longitude'], lon)
        self.assertAlmostEqual(result['latitude'], lat)

    def test_round_trip_latitude_first(self):
        lon, lat = -73.935242, 40.730610
        point_str = Point.to_point_str(lon, lat, latitude_first=True)
        result = Point.from_point_str(point_str, latitude_first=True)
        self.assertAlmostEqual(result['longitude'], lon)
        self.assertAlmostEqual(result['latitude'], lat)

    def test_negative_coordinates(self):
        result = Point.from_point_str('POINT(-73.935242 40.730610)')
        self.assertAlmostEqual(result['longitude'], -73.935242)
        self.assertAlmostEqual(result['latitude'], 40.730610)

    def test_zero_coordinates(self):
        self.assertEqual(Point.to_point_str(0.0, 0.0), 'POINT(0.0 0.0)')
        result = Point.from_point_str('POINT(0.0 0.0)')
        self.assertEqual(result, {'longitude': 0.0, 'latitude': 0.0})
