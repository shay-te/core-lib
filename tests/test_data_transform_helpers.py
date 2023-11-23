import enum
import unittest

from core_lib.data_transform.helpers import get_dict_attr, set_dict_attr, enum_to_dict


class TestHelpers(unittest.TestCase):
    data = {
        'person': {
            'name': 'person',
            'age': 131,
            'object': {
                'person2': {
                    'name': 'person2',
                    'age': 478,
                    'object': {
                        'person': {
                            'name': 'person3',
                            'age': 789,
                        }
                    },
                }
            },
        }
    }

    def test_get_attr(self):
        value = get_dict_attr(self.data, 'person.object.person2.object.person')
        self.assertDictEqual(value, self.data['person']['object']['person2']['object']['person'])
        value = get_dict_attr(self.data, 'person.object.person2.object.person.name')
        self.assertEqual(value, self.data['person']['object']['person2']['object']['person']['name'])
        value = get_dict_attr(self.data, 'person.object')
        self.assertDictEqual(value, self.data['person']['object'])
        value = get_dict_attr(self.data, 'person.object.person2')
        self.assertDictEqual(value, self.data['person']['object']['person2'])

        self.assertIsNone(get_dict_attr(self.data, 'person.object.person'))
        self.assertDictEqual({}, get_dict_attr(self.data, 'person.object.person', {}))
        self.assertListEqual([], get_dict_attr(self.data, 'person.object.person', []))
        self.assertFalse(get_dict_attr(self.data, 'person.object.person', False))

    def test_set_attr(self):
        test_obj = {'name': 'some_name'}
        test_value = 'some_value'
        test_name = 'new_name'
        test_age = 1234

        set_dict_attr(self.data, 'person.object.person2.object.person.name', test_name)
        self.assertEqual(self.data['person']['object']['person2']['object']['person']['name'], test_name)
        set_dict_attr(self.data, 'person.object.person2.object.person.age', test_age)
        self.assertEqual(self.data['person']['object']['person2']['object']['person']['age'], test_age)
        set_dict_attr(self.data, 'person.object.person2.object.person', test_value)
        self.assertEqual(self.data['person']['object']['person2']['object']['person'], test_value)
        set_dict_attr(self.data, 'person.object.person2.object.person', test_obj)
        self.assertDictEqual(self.data['person']['object']['person2']['object']['person'], test_obj)
        set_dict_attr(self.data, 'person.object.person2.object', test_obj)
        self.assertDictEqual(self.data['person']['object']['person2']['object'], test_obj)
        set_dict_attr(self.data, 'person.object', test_obj)
        self.assertDictEqual(self.data['person']['object'], test_obj)
        set_dict_attr(self.data, 'person', test_name)
        self.assertEqual(self.data['person'], test_name)
        set_dict_attr(self.data, 'person', test_obj)
        self.assertDictEqual(self.data['person'], test_obj)

        value = set_dict_attr({}, 'key1.key2.key3.key4', test_value)
        self.assertEqual(value['key1']['key2']['key3']['key4'], test_value)
        set_dict_attr(value, 'key1', test_value)
        self.assertEqual(value['key1'], test_value)

    def test_enums_to_dict(self):
        class Animals(enum.Enum):
            DOG = 1
            CAT = 2
            BAT = 3

        class CarsTypes(enum.Enum):
            BMW = 0
            TOYOTA = 1
            VOLVO = 2

        converted_enum = enum_to_dict(Animals)
        self.assertDictEqual(converted_enum, {
            Animals.DOG.name: Animals.DOG.value,
            Animals.CAT.name: Animals.CAT.value,
            Animals.BAT.name: Animals.BAT.value,
        })
        converted_enum = enum_to_dict(CarsTypes)
        self.assertDictEqual(converted_enum, {
            CarsTypes.BMW.name: CarsTypes.BMW.value,
            CarsTypes.TOYOTA.name: CarsTypes.TOYOTA.value,
            CarsTypes.VOLVO.name: CarsTypes.VOLVO.value,
        })
