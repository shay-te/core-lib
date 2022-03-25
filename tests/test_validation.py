import enum
import unittest

from core_lib.helpers.validation import is_bool, is_float, is_int, is_email, is_int_enum, is_url


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
        self.assertEqual(is_bool(None), False)

    def test_float(self):
        self.assertEqual(is_float(0.0014), True)
        self.assertEqual(is_float(14), True)
        self.assertEqual(is_float("0.0014"), True)
        self.assertEqual(is_float("14"), True)
        self.assertEqual(is_float("NaN"), True)
        self.assertEqual(is_float("strings here"), False)
        self.assertEqual(is_float((1, 2, 3)), False)
        self.assertEqual(is_float([1, 2, 3]), False)
        self.assertEqual(is_float({1, 2, 3}), False)
        self.assertEqual(is_float(None), False)

    def test_int(self):
        self.assertEqual(is_int(0.0014), True)
        self.assertEqual(is_int(14), True)
        self.assertEqual(is_int("0.0014"), False)
        self.assertEqual(is_int("14"), True)
        self.assertEqual(is_int("NaN"), False)
        self.assertEqual(is_int("strings here"), False)
        self.assertEqual(is_int((1, 2, 3)), False)
        self.assertEqual(is_int([1, 2, 3]), False)
        self.assertEqual(is_int({1, 2, 3}), False)
        self.assertEqual(is_int(None), False)

    def test_email(self):
        self.assertEqual(is_email("abc@xyz.com"), True)
        self.assertEqual(is_email("abc.def@xyz.com"), True)
        self.assertEqual(is_email("example.firstname-lastname@email.com"), True)
        self.assertEqual(is_email("example@email.co.jp"), True)
        self.assertEqual(is_email("example@email.museum"), True)
        self.assertEqual(is_email("example@email.name"), True)
        self.assertEqual(is_email("_______@email.com"), True)
        self.assertEqual(is_email("example@email-one.com"), True)
        self.assertEqual(is_email("example+firstname+lastname@email.com"), True)
        self.assertEqual(is_email("example.first.middle.lastname@email.com"), True)
        self.assertEqual(is_email("0987654321@example.com"), True)
        self.assertEqual(
            is_email("ljksfdghjskfdhgjklsdfhgjks0987654321@asdfasdfasdfasdfasfasdfaexample." "casdfadsfasdfgasdfasdom"),
            True,
        )
        self.assertEqual(is_email('"email"@example.com'), False)
        self.assertEqual(is_email(None), False)
        self.assertEqual(is_email(""), False)
        self.assertEqual(is_email("   "), False)
        self.assertEqual(is_email("as;fj123.df@asdfa/c.vcom"), False)
        self.assertEqual(is_email("very.”(),:;<>[]”.VERY.”very@\\ \"very”.unusual@strange.example.com"), False)
        self.assertEqual(is_email("<asd>>@strange.com"), False)

    def test_enum(self):
        self.assertEqual(is_int_enum(MyEnum.one.value, MyEnum), True)
        self.assertEqual(is_int_enum(MyEnum.two.value, MyEnum), True)
        self.assertEqual(is_int_enum(MyEnum.three.value, MyEnum), True)
        self.assertEqual(is_int_enum(None, MyEnum), False)
        self.assertEqual(is_int_enum(11, MyEnum), False)
        self.assertEqual(is_int_enum(11, 'MyEnum'), False)

    def test_url(self):
        self.assertEqual(is_url('http://domian.com'), True)
        self.assertEqual(is_url('https://domian.com'), True)
        self.assertEqual(is_url('https://www.domian.com'), True)
        self.assertEqual(is_url('http://domian.com.co.uk'), True)
        self.assertEqual(is_url('https://192.168.0.0.com'), True)
        self.assertEqual(is_url('https://subdomain.domain.com'), True)
        self.assertEqual(is_url('ftp://domian.com'), False)
        self.assertEqual(is_url('random://domain.com'), False)
        self.assertEqual(is_url('telnet://domain.com'), False)
        self.assertEqual(is_url('subdomain.domain.com'), False)
        self.assertEqual(is_url('domain.com'), False)
        self.assertEqual(is_url('hello world'), False)
        self.assertEqual(is_url('192.168.0.0'), False)
        self.assertEqual(is_url('12345'), False)
        self.assertEqual(is_url('http://domian'), False)
        self.assertEqual(is_url('http://'), False)
