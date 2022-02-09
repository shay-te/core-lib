import enum
import unittest
from datetime import datetime, date

from geoalchemy2 import WKTElement

from core_lib.registry.default_registry import DefaultRegistry


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class TestDefaultRegistry(unittest.TestCase):

    def test_default_registry_string(self):
        string = 'hello world'
        registry_factory = DefaultRegistry(str)
        registry_factory.register('string', string)

        with self.assertRaises(ValueError):
            registry_factory.register('string', 10)
        with self.assertRaises(AssertionError):
            registry_factory.register('string', None)
        with self.assertRaises(AssertionError):
            registry_factory.register('string', '')

        self.assertEqual(registry_factory.get('string'), string)
        self.assertEqual(registry_factory.get(), string)

        self.assertEqual(registry_factory.registered()[0], 'string')
        self.assertListEqual(registry_factory.registered(), ['string'])

        registry_factory.unregister('string')
        self.assertEqual(registry_factory.get('string'), None)

    def test_default_registry_int(self):
        integer = 145
        registry_factory = DefaultRegistry(int)
        registry_factory.register('integer', integer)

        with self.assertRaises(ValueError):
            registry_factory.register('integer', 'Hello')
        with self.assertRaises(ValueError):
            registry_factory.register('integer', 12.01147)
        with self.assertRaises(AssertionError):
            registry_factory.register('integer', None)
        with self.assertRaises(AssertionError):
            registry_factory.register('integer', {})

        self.assertEqual(registry_factory.get('integer'), integer)
        self.assertEqual(registry_factory.get(), integer)

        self.assertEqual(registry_factory.registered()[0], 'integer')
        self.assertListEqual(registry_factory.registered(), ['integer'])

        registry_factory.unregister('integer')
        self.assertEqual(registry_factory.get('integer'), None)

    def test_default_registry_float(self):
        flt = 145.67
        registry_factory = DefaultRegistry(float)
        registry_factory.register('float', flt)

        with self.assertRaises(ValueError):
            registry_factory.register('float', 'Hello')
        with self.assertRaises(ValueError):
            registry_factory.register('float', 12)
        with self.assertRaises(AssertionError):
            registry_factory.register('float', None)
        with self.assertRaises(AssertionError):
            registry_factory.register('float', {})

        self.assertEqual(registry_factory.get('float'), flt)
        self.assertEqual(registry_factory.get(), flt)

        self.assertEqual(registry_factory.registered()[0], 'float')
        self.assertListEqual(registry_factory.registered(), ['float'])

        registry_factory.unregister('float')
        self.assertEqual(registry_factory.get('float'), None)

    def test_default_registry_bool(self):
        boolean = True
        registry_factory = DefaultRegistry(bool)
        registry_factory.register('boolean', boolean)

        with self.assertRaises(ValueError):
            registry_factory.register('boolean', 'Hello')
        with self.assertRaises(ValueError):
            registry_factory.register('boolean', 12)
        with self.assertRaises(AssertionError):
            registry_factory.register('boolean', None)
        with self.assertRaises(AssertionError):
            registry_factory.register('boolean', {})

        self.assertEqual(registry_factory.get('boolean'), boolean)
        self.assertEqual(registry_factory.get(), boolean)

        self.assertEqual(registry_factory.registered()[0], 'boolean')
        self.assertListEqual(registry_factory.registered(), ['boolean'])

        registry_factory.unregister('boolean')
        self.assertEqual(registry_factory.get('boolean'), None)

    def test_default_registry_list(self):
        lst = [['fruit', 'apple'], ['fruit', 'banana'], ['fruit', 'cherry']]
        registry_factory = DefaultRegistry(list)
        registry_factory.register('list', lst)

        with self.assertRaises(ValueError):
            registry_factory.register('list', 'Hello')
        with self.assertRaises(ValueError):
            registry_factory.register('list', 12)
        with self.assertRaises(AssertionError):
            registry_factory.register('list', None)
        with self.assertRaises(AssertionError):
            registry_factory.register('list', {})

        self.assertListEqual(registry_factory.get('list'), lst)
        self.assertListEqual(registry_factory.get(), lst)

        self.assertEqual(registry_factory.registered()[0], 'list')
        self.assertListEqual(registry_factory.registered(), ['list'])

        registry_factory.unregister('list')
        self.assertEqual(registry_factory.get('list'), None)

    def test_default_registry_tuple(self):
        tpl = (('fruit', 'apple'), ('fruit', 'banana'), ('fruit', 'cherry'))
        registry_factory = DefaultRegistry(tuple)
        registry_factory.register('tuple', tpl)

        with self.assertRaises(ValueError):
            registry_factory.register('tuple', 'Hello')
        with self.assertRaises(ValueError):
            registry_factory.register('tuple', 12)
        with self.assertRaises(AssertionError):
            registry_factory.register('tuple', None)
        with self.assertRaises(AssertionError):
            registry_factory.register('tuple', {})

        self.assertTupleEqual(registry_factory.get('tuple'), tpl)
        self.assertTupleEqual(registry_factory.get(), tpl)

        self.assertEqual(registry_factory.registered()[0], 'tuple')
        self.assertListEqual(registry_factory.registered(), ['tuple'])

        registry_factory.unregister('tuple')
        self.assertEqual(registry_factory.get('tuple'), None)

    def test_default_registry_dict(self):
        dat = date(2022, 1, 1)
        dattime = datetime(2022, 1, 1)
        tpl = ('fruit', 'apple')
        lst = ['fruit', 'apple']
        point = WKTElement('POINT(5 45)')
        dct = {
            'date': dat,
            'datetime': dattime,
            'tuple': tpl,
            'list': lst,
            'point': point,
            'enum': MyEnum.one.value
        }
        registry_factory = DefaultRegistry(dict)
        registry_factory.register('dict', dct)

        with self.assertRaises(ValueError):
            registry_factory.register('dict', 'Hello')
        with self.assertRaises(ValueError):
            registry_factory.register('dict', 12)
        with self.assertRaises(AssertionError):
            registry_factory.register('dict', None)
        with self.assertRaises(AssertionError):
            registry_factory.register('dict', ())

        self.assertDictEqual(registry_factory.get('dict'), dct)
        self.assertDictEqual(registry_factory.get(), dct)
        self.assertEqual(registry_factory.get('dict')['date'], dat)
        self.assertEqual(registry_factory.get('dict')['datetime'], dattime)
        self.assertEqual(registry_factory.get('dict')['tuple'], tpl)
        self.assertEqual(registry_factory.get('dict')['list'], lst)
        self.assertEqual(registry_factory.get('dict')['point'], point)
        self.assertEqual(registry_factory.get('dict')['enum'], 1)

        self.assertEqual(registry_factory.registered()[0], 'dict')
        self.assertListEqual(registry_factory.registered(), ['dict'])

        registry_factory.unregister('dict')
        self.assertEqual(registry_factory.get('dict'), None)

    def test_default_registry_multiple_default(self):
        registry_factory = DefaultRegistry(str)

        string_1 = 'hello world 1'
        registry_factory.register('string_1', string_1)

        string_2 = 'hello world 2'
        registry_factory.register('string_2', string_2, is_default=True)

        string_3 = 'hello world 3'
        registry_factory.register('string_3', string_3)

        self.assertEqual(registry_factory.get('string_1'), string_1)
        self.assertEqual(registry_factory.get('string_2'), string_2)
        self.assertEqual(registry_factory.get('string_3'), string_3)

        self.assertEqual(registry_factory.get(), string_2)
        self.assertNotEqual(registry_factory.get(), string_1)
        self.assertNotEqual(registry_factory.get(), string_3)

        self.assertEqual(registry_factory.registered()[0], 'string_1')
        self.assertEqual(registry_factory.registered()[1], 'string_2')
        self.assertEqual(registry_factory.registered()[2], 'string_3')

        self.assertListEqual(registry_factory.registered(), ['string_1', 'string_2', 'string_3'])

        registry_factory.unregister('string_2')
        self.assertEqual(registry_factory.get(), string_1)

    def test_default_registry_multiple_objects_default(self):
        registry_factory = DefaultRegistry(dict)

        dict_1 = {'number': 'one'}
        registry_factory.register('dict_1', dict_1)

        dict_2 = {'number': 'two'}
        registry_factory.register('dict_2', dict_2, is_default=True)

        dict_3 = {'number': 'three'}
        registry_factory.register('dict_3', dict_3)

        self.assertDictEqual(registry_factory.get('dict_1'), dict_1)
        self.assertEqual(registry_factory.get('dict_1')['number'], 'one')
        self.assertDictEqual(registry_factory.get('dict_2'), dict_2)
        self.assertEqual(registry_factory.get('dict_2')['number'], 'two')
        self.assertDictEqual(registry_factory.get('dict_3'), dict_3)
        self.assertEqual(registry_factory.get('dict_3')['number'], 'three')

        self.assertDictEqual(registry_factory.get(), dict_2)
        self.assertNotEqual(registry_factory.get(), dict_1)
        self.assertNotEqual(registry_factory.get(), dict_3)

        self.assertEqual(registry_factory.registered()[0], 'dict_1')
        self.assertEqual(registry_factory.registered()[1], 'dict_2')
        self.assertEqual(registry_factory.registered()[2], 'dict_3')

        self.assertListEqual(registry_factory.registered(), ['dict_1', 'dict_2', 'dict_3'])

        registry_factory.unregister('dict_2')
        self.assertEqual(registry_factory.get(), dict_1)
