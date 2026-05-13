import unittest
from unittest.mock import MagicMock, patch

from shapely.geometry import Point as ShapelyPoint

from core_lib.data_layers.data.db.sqlalchemy.types.point import Point


class TestPoint(unittest.TestCase):
    def test_get_col_spec(self):
        self.assertEqual(Point().get_col_spec(), 'POINT')

    def test_bind_expression(self):
        expr = Point().bind_expression('value')
        self.assertIsNotNone(expr)

    def test_column_expression(self):
        col = MagicMock()
        out = Point().column_expression(col)
        self.assertIsNotNone(out)

    def test_from_point_wkb(self):
        wkb = MagicMock()
        with patch(
            'core_lib.data_layers.data.db.sqlalchemy.types.point.to_shape'
        ) as mock_to_shape:
            mock_to_shape.return_value = ShapelyPoint(20.0, 10.0)
            result = Point.from_point_wkb(wkb)
            self.assertEqual(result, {'longitude': 20.0, 'latitude': 10.0})

    def test_from_point_str_latitude_first(self):
        self.assertEqual(
            Point.from_point_str('POINT(10.0 20.0)', latitude_first=True),
            {'latitude': 10.0, 'longitude': 20.0},
        )

    def test_to_point_str_latitude_first(self):
        self.assertEqual(Point.to_point_str(20.0, 10.0, latitude_first=True), 'POINT(10.0 20.0)')

    def test_to_point_str_default(self):
        self.assertEqual(Point.to_point_str(20.0, 10.0), 'POINT(20.0 10.0)')
