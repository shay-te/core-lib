import enum
import unittest
from datetime import datetime, date

from geoalchemy2 import WKTElement

from core_lib.core_lib import CoreLib
from core_lib.registry.default_registry import DefaultRegistry


class Customer(object):
    pass


class CustomerRegistry(DefaultRegistry):
    def __init__(self):
        DefaultRegistry.__init__(self, Customer)


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class TestDefaultRegistry(unittest.TestCase):
    def test_default_registry_string(self):
        string = 'hello world'
        str_registry = DefaultRegistry(str)
        str_registry.register('string', string)

        with self.assertRaises(ValueError):
            str_registry.register('string', 10)
        with self.assertRaises(AssertionError):
            str_registry.register('string', None)
        with self.assertRaises(AssertionError):
            str_registry.register('string', '')

        self.assertEqual(str_registry.get('string'), string)
        self.assertEqual(str_registry.get(), string)

        self.assertEqual(str_registry.registered()[0], 'string')
        self.assertListEqual(str_registry.registered(), ['string'])

        str_registry.unregister('string')
        self.assertEqual(str_registry.get('string'), None)

    def test_default_registry_int(self):
        integer = 145
        int_registry = DefaultRegistry(int)
        int_registry.register('integer', integer)

        with self.assertRaises(ValueError):
            int_registry.register('integer', 'Hello')
        with self.assertRaises(ValueError):
            int_registry.register('integer', 12.01147)
        with self.assertRaises(AssertionError):
            int_registry.register('integer', None)
        with self.assertRaises(AssertionError):
            int_registry.register('integer', {})

        self.assertEqual(int_registry.get('integer'), integer)
        self.assertEqual(int_registry.get(), integer)

        self.assertEqual(int_registry.registered()[0], 'integer')
        self.assertListEqual(int_registry.registered(), ['integer'])

        int_registry.unregister('integer')
        self.assertEqual(int_registry.get('integer'), None)

    def test_default_registry_float(self):
        flt = 145.67
        float_registry = DefaultRegistry(float)
        float_registry.register('float', flt)

        with self.assertRaises(ValueError):
            float_registry.register('float', 'Hello')
        with self.assertRaises(ValueError):
            float_registry.register('float', 12)
        with self.assertRaises(AssertionError):
            float_registry.register('float', None)
        with self.assertRaises(AssertionError):
            float_registry.register('float', {})

        self.assertEqual(float_registry.get('float'), flt)
        self.assertEqual(float_registry.get(), flt)

        self.assertEqual(float_registry.registered()[0], 'float')
        self.assertListEqual(float_registry.registered(), ['float'])

        float_registry.unregister('float')
        self.assertEqual(float_registry.get('float'), None)

    def test_default_registry_bool(self):
        boolean = True
        bool_registry = DefaultRegistry(bool)
        bool_registry.register('boolean', boolean)

        with self.assertRaises(ValueError):
            bool_registry.register('boolean', 'Hello')
        with self.assertRaises(ValueError):
            bool_registry.register('boolean', 12)
        with self.assertRaises(AssertionError):
            bool_registry.register('boolean', None)
        with self.assertRaises(AssertionError):
            bool_registry.register('boolean', {})

        self.assertEqual(bool_registry.get('boolean'), boolean)
        self.assertEqual(bool_registry.get(), boolean)

        self.assertEqual(bool_registry.registered()[0], 'boolean')
        self.assertListEqual(bool_registry.registered(), ['boolean'])

        bool_registry.unregister('boolean')
        self.assertEqual(bool_registry.get('boolean'), None)

    def test_default_registry_list(self):
        lst = [['fruit', 'apple'], ['fruit', 'banana'], ['fruit', 'cherry']]
        list_registry = DefaultRegistry(list)
        list_registry.register('list', lst)

        with self.assertRaises(ValueError):
            list_registry.register('list', 'Hello')
        with self.assertRaises(ValueError):
            list_registry.register('list', 12)
        with self.assertRaises(AssertionError):
            list_registry.register('list', None)
        with self.assertRaises(AssertionError):
            list_registry.register('list', {})

        self.assertListEqual(list_registry.get('list'), lst)
        self.assertListEqual(list_registry.get(), lst)

        self.assertEqual(list_registry.registered()[0], 'list')
        self.assertListEqual(list_registry.registered(), ['list'])

        list_registry.unregister('list')
        self.assertEqual(list_registry.get('list'), None)

    def test_default_registry_tuple(self):
        tpl = (('fruit', 'apple'), ('fruit', 'banana'), ('fruit', 'cherry'))
        tuple_registry = DefaultRegistry(tuple)
        tuple_registry.register('tuple', tpl)

        with self.assertRaises(ValueError):
            tuple_registry.register('tuple', 'Hello')
        with self.assertRaises(ValueError):
            tuple_registry.register('tuple', 12)
        with self.assertRaises(AssertionError):
            tuple_registry.register('tuple', None)
        with self.assertRaises(AssertionError):
            tuple_registry.register('tuple', {})

        self.assertTupleEqual(tuple_registry.get('tuple'), tpl)
        self.assertTupleEqual(tuple_registry.get(), tpl)

        self.assertEqual(tuple_registry.registered()[0], 'tuple')
        self.assertListEqual(tuple_registry.registered(), ['tuple'])

        tuple_registry.unregister('tuple')
        self.assertEqual(tuple_registry.get('tuple'), None)

    def test_default_registry_dict(self):
        dat = date(2022, 1, 1)
        dattime = datetime(2022, 1, 1)
        tpl = ('fruit', 'apple')
        lst = ['fruit', 'apple']
        point = WKTElement('POINT(5 45)')
        dct = {'date': dat, 'datetime': dattime, 'tuple': tpl, 'list': lst, 'point': point, 'enum': MyEnum.one.value}
        dict_registry = DefaultRegistry(dict)
        dict_registry.register('dict', dct)

        with self.assertRaises(ValueError):
            dict_registry.register('dict', 'Hello')
        with self.assertRaises(ValueError):
            dict_registry.register('dict', 12)
        with self.assertRaises(AssertionError):
            dict_registry.register('dict', None)
        with self.assertRaises(AssertionError):
            dict_registry.register('dict', ())

        self.assertDictEqual(dict_registry.get('dict'), dct)
        self.assertDictEqual(dict_registry.get(), dct)
        self.assertEqual(dict_registry.get('dict')['date'], dat)
        self.assertEqual(dict_registry.get('dict')['datetime'], dattime)
        self.assertEqual(dict_registry.get('dict')['tuple'], tpl)
        self.assertEqual(dict_registry.get('dict')['list'], lst)
        self.assertEqual(dict_registry.get('dict')['point'], point)
        self.assertEqual(dict_registry.get('dict')['enum'], 1)

        self.assertEqual(dict_registry.registered()[0], 'dict')
        self.assertListEqual(dict_registry.registered(), ['dict'])

        dict_registry.unregister('dict')
        self.assertEqual(dict_registry.get('dict'), None)

    def test_default_registry_multiple_default(self):
        multiple_registry = DefaultRegistry(str)

        string_1 = 'hello world 1'
        multiple_registry.register('string_1', string_1)

        string_2 = 'hello world 2'
        multiple_registry.register('string_2', string_2, is_default=True)

        string_3 = 'hello world 3'
        multiple_registry.register('string_3', string_3)

        self.assertEqual(multiple_registry.get('string_1'), string_1)
        self.assertEqual(multiple_registry.get('string_2'), string_2)
        self.assertEqual(multiple_registry.get('string_3'), string_3)

        self.assertEqual(multiple_registry.get(), string_2)
        self.assertNotEqual(multiple_registry.get(), string_1)
        self.assertNotEqual(multiple_registry.get(), string_3)

        self.assertEqual(multiple_registry.registered()[0], 'string_1')
        self.assertEqual(multiple_registry.registered()[1], 'string_2')
        self.assertEqual(multiple_registry.registered()[2], 'string_3')

        self.assertListEqual(multiple_registry.registered(), ['string_1', 'string_2', 'string_3'])

        multiple_registry.unregister('string_2')
        self.assertEqual(multiple_registry.get(), string_1)

    def test_default_registry_multiple_objects_default(self):
        multiple_registry = DefaultRegistry(dict)

        dict_1 = {'number': 'one'}
        multiple_registry.register('dict_1', dict_1)

        dict_2 = {'number': 'two'}
        multiple_registry.register('dict_2', dict_2, is_default=True)

        dict_3 = {'number': 'three'}
        multiple_registry.register('dict_3', dict_3)

        self.assertDictEqual(multiple_registry.get('dict_1'), dict_1)
        self.assertEqual(multiple_registry.get('dict_1')['number'], 'one')
        self.assertDictEqual(multiple_registry.get('dict_2'), dict_2)
        self.assertEqual(multiple_registry.get('dict_2')['number'], 'two')
        self.assertDictEqual(multiple_registry.get('dict_3'), dict_3)
        self.assertEqual(multiple_registry.get('dict_3')['number'], 'three')

        self.assertDictEqual(multiple_registry.get(), dict_2)
        self.assertNotEqual(multiple_registry.get(), dict_1)
        self.assertNotEqual(multiple_registry.get(), dict_3)

        self.assertEqual(multiple_registry.registered()[0], 'dict_1')
        self.assertEqual(multiple_registry.registered()[1], 'dict_2')
        self.assertEqual(multiple_registry.registered()[2], 'dict_3')

        self.assertListEqual(multiple_registry.registered(), ['dict_1', 'dict_2', 'dict_3'])

        multiple_registry.unregister('dict_2')
        self.assertEqual(multiple_registry.get(), dict_1)

    def test_complex_data(self):
        customer_registry = CustomerRegistry()

        customer_a = Customer()
        customer_registry.register('customer_a', customer_a)

        customer_b = Customer()
        customer_registry.register('customer_b', customer_b, is_default=True)

        customer_c = Customer()
        customer_registry.register('customer_c', customer_c)

        self.assertEqual(customer_registry.get('customer_a'), customer_a)
        self.assertEqual(customer_registry.get('customer_b'), customer_b)
        self.assertEqual(customer_registry.get('customer_c'), customer_c)

        self.assertEqual(customer_registry.get(), customer_b)
        self.assertNotEqual(customer_registry.get(), customer_a)
        self.assertNotEqual(customer_registry.get(), customer_c)

        self.assertEqual(customer_registry.registered()[0], 'customer_a')
        self.assertEqual(customer_registry.registered()[1], 'customer_b')
        self.assertEqual(customer_registry.registered()[2], 'customer_c')

        self.assertListEqual(customer_registry.registered(), ['customer_a', 'customer_b', 'customer_c'])

        customer_registry.unregister('customer_b')
        self.assertEqual(customer_registry.get(), customer_a)
