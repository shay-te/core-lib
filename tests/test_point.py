"""Point is a spatial POINT column type plus WKT helpers: the column is created as POINT, a write is wrapped in
ST_GeomFromText(), a read in ST_AsText(), and the helpers convert between coordinates and a WKT `POINT(x y)` string
or the geoalchemy2 WKBElement a Geometry('POINT') column returns."""
import unittest

from geoalchemy2.shape import from_shape
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import Column, Integer, create_engine, insert, select, text
from sqlalchemy.orm import declarative_base

from core_lib.data_layers.data.db.sqlalchemy.types.point import Point

# A base of its own, so this table never joins core-lib's shared Base.metadata.
LocalBase = declarative_base()


class Location(LocalBase):
    __tablename__ = 'acme_location'

    id = Column(Integer, primary_key=True)
    coordinates = Column(Point())


class TestPoint(unittest.TestCase):

    def test_column_is_created_as_point(self):
        engine = create_engine('sqlite://')
        try:
            LocalBase.metadata.create_all(engine)
            with engine.connect() as connection:
                columns = connection.execute(text(f'PRAGMA table_info({Location.__tablename__})')).fetchall()
        finally:
            engine.dispose()

        declared_types = {column.name: column.type for column in columns}
        self.assertEqual('POINT', declared_types[Location.coordinates.key])

    def test_write_is_wrapped_in_st_geom_from_text(self):
        statement = insert(Location).values({Location.coordinates.key: Point.to_point_str(34.7818, 32.0853)})

        table, column = Location.__tablename__, Location.coordinates.key
        self.assertEqual(f'INSERT INTO {table} ({column}) VALUES (ST_GeomFromText(:{column}))', str(statement))

    def test_read_is_wrapped_in_st_as_text(self):
        statement = select(Location.coordinates)

        table, column = Location.__tablename__, Location.coordinates.key
        self.assertEqual(f'SELECT ST_AsText({table}.{column}) AS {column} \nFROM {table}', str(statement))

    def test_to_point_str_writes_longitude_first_unless_asked(self):
        self.assertEqual('POINT(34.7818 32.0853)', Point.to_point_str(longitude=34.7818, latitude=32.0853))
        self.assertEqual(
            'POINT(32.0853 34.7818)', Point.to_point_str(longitude=34.7818, latitude=32.0853, latitude_first=True)
        )

    def test_from_point_str_reads_the_order_it_is_told(self):
        self.assertEqual({'longitude': 34.7818, 'latitude': 32.0853}, Point.from_point_str('POINT(34.7818 32.0853)'))
        self.assertEqual(
            {'latitude': 34.7818, 'longitude': 32.0853},
            Point.from_point_str('POINT(34.7818 32.0853)', latitude_first=True),
        )

    def test_from_point_str_reads_wkt_with_a_space_after_point(self):
        self.assertEqual({'longitude': 34.7818, 'latitude': 32.0853}, Point.from_point_str('POINT (34.7818 32.0853)'))
        # shapely writes WKT that way
        self.assertEqual(
            {'longitude': -0.1278, 'latitude': 51.5074}, Point.from_point_str(ShapelyPoint(-0.1278, 51.5074).wkt)
        )

    def test_negative_coordinates_keep_their_sign(self):
        self.assertEqual('POINT(-0.1278 -51.5074)', Point.to_point_str(longitude=-0.1278, latitude=-51.5074))
        self.assertEqual(
            {'latitude': -51.5074, 'longitude': -0.1278},
            Point.from_point_str('POINT(-51.5074 -0.1278)', latitude_first=True),
        )

    def test_from_point_wkb_reads_a_geometry_column_value(self):
        geometry_value = from_shape(ShapelyPoint(34.7818, 32.0853))  # the WKBElement a Geometry('POINT') column holds

        self.assertEqual({'latitude': 32.0853, 'longitude': 34.7818}, Point.from_point_wkb(geometry_value))
