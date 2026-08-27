import enum
import unittest

from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class TestIntEnum(unittest.TestCase):
    def setUp(self):
        self.col_type = IntEnum(Color)

    def test_bind_param_returns_int_value(self):
        self.assertEqual(self.col_type.process_bind_param(Color.RED, None), 1)
        self.assertEqual(self.col_type.process_bind_param(Color.GREEN, None), 2)
        self.assertEqual(self.col_type.process_bind_param(Color.BLUE, None), 3)

    def test_bind_param_none_returns_none(self):
        self.assertIsNone(self.col_type.process_bind_param(None, None))

    def test_result_value_returns_enum_member(self):
        self.assertEqual(self.col_type.process_result_value(1, None), Color.RED)
        self.assertEqual(self.col_type.process_result_value(2, None), Color.GREEN)
        self.assertEqual(self.col_type.process_result_value(3, None), Color.BLUE)

    def test_result_value_none_returns_none(self):
        self.assertIsNone(self.col_type.process_result_value(None, None))

    def test_result_value_invalid_raises(self):
        self.assertRaises(ValueError, self.col_type.process_result_value, 99, None)

    def test_round_trip(self):
        for member in Color:
            stored = self.col_type.process_bind_param(member, None)
            restored = self.col_type.process_result_value(stored, None)
            self.assertEqual(restored, member)
