import enum
import unittest

from core_lib.helpers.validation import is_bool, is_float, is_int, is_email, is_int_enum


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class TestValidations(unittest.TestCase):

    def test_bool(self):
        self.assertEqual(is_bool("True"), True)
        self.assertEqual(is_bool(True), True)
        self.assertEqual(is_bool("False"), True)
        self.assertEqual(is_bool(False), True)
        self.assertEqual(is_bool("string"), False)
        self.assertEqual(is_bool(14), False)
        self.assertEqual(is_bool({"data": "data"}), False)

    def test_float(self):
        self.assertEqual(is_float(0.0014), True)
        self.assertEqual(is_float(14), True)
        self.assertEqual(is_float("0.0014"), True)
        self.assertEqual(is_float("14"), True)
        self.assertEqual(is_float("NaN"), True)
        self.assertEqual(is_float("strings here"), False)

    def test_int(self):
        self.assertEqual(is_int(0.0014), True)
        self.assertEqual(is_int(14), True)
        self.assertEqual(is_int("0.0014"), False)
        self.assertEqual(is_int("14"), True)
        self.assertEqual(is_int("NaN"), False)
        self.assertEqual(is_int("strings here"), False)

    def test_email(self):
        self.assertEqual(is_email("abc@xyz.com"), True)
        self.assertEqual(is_email("abc.def@xyz.com"), True)
        self.assertEqual(is_email("abc.def"), False)

    def test_enum(self):
        self.assertEqual(is_int_enum(MyEnum.one, MyEnum), True)
        self.assertEqual(is_int_enum(MyEnum.two, MyEnum), True)
        self.assertEqual(is_int_enum(MyEnum.three, MyEnum), True)
