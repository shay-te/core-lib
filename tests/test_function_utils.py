import datetime
import enum
import unittest

from geoalchemy2 import WKTElement

from core_lib.helpers.func_utils import (
    build_function_key,
    get_func_parameters_as_dict,
    get_func_parameter_index_by_name,
    Keyable,
)


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class User(Keyable):
    def __init__(self, u_id, name):
        self.id = u_id
        self.name = name

    def key(self) -> str:
        return f'User(id:{self.id}, name:{self.name})'


class TestFunctionUtils(unittest.TestCase):
    def test_cache_generates_key(self):
        def function_with_params(param_1, param_2, param_3=11, param_4=22):
            return 1

        key1 = build_function_key('asdfghjklzxcvbnm', function_with_params, *[1234, 12345134], **{})
        self.assertNotEqual(key1, None)
        self.assertEqual(key1, 'asdfghjklzxcvbnm')

        key2 = build_function_key('xyz_{param_1}_{param_2}', function_with_params, *[11, 22], **{})
        self.assertNotEqual(key2, None)
        self.assertEqual(key2, 'xyz_11_22')

        key3 = build_function_key('xyz_{param_1}_{param_2}', function_with_params, *[11], **{})
        self.assertNotEqual(key3, None)
        self.assertEqual(key3, 'xyz_11_!Eparam_2E!')

        key4 = build_function_key('xyz_{param_1}_{param_2}', function_with_params, *[], **{'param_2': 'pp2'})
        self.assertNotEqual(key4, None)
        self.assertEqual(key4, 'xyz_!Eparam_1E!_pp2')

        key5 = build_function_key('xyz_{param_1}_{param_2}', function_with_params, 1, 2)
        self.assertNotEqual(key5, None)
        self.assertEqual(key5, 'xyz_1_2')

        key6 = build_function_key('xyz_{param_1}_{param_2}', function_with_params, None, None)
        self.assertNotEqual(key6, None)
        self.assertEqual(key6, 'xyz_!Eparam_1E!_!Eparam_2E!')

        dat = datetime.date(2022, 1, 1)
        dattime = datetime.datetime(2022, 1, 1)
        tpl = ("fruit", "apple")
        lst = ["fruit", "apple"]
        point = WKTElement('POINT(5 45)')
        set_value = {"fruit", "apple"}
        obj = {"fruit1": "apple", "fruit2": "orange"}
        string = 'Jon\n\r Doe'

        def function_with_multi_params(
            param_1,
            param_2,
            param_3,
            param_4,
            param_5,
            param_6,
            param_7=point,
            param_8=set_value,
            param_9=MyEnum.one.value,
        ):
            pass

        key7 = build_function_key(
            'xyz_{param_1}_{param_2}_{param_3}_{param_4}_{param_5}_{param_6}_{param_7}_{param_8}_{param_9}',
            function_with_multi_params,
            dat,
            dattime,
            tpl,
            lst,
            obj,
            string,
        )
        self.assertNotEqual(key7, None)
        self.assertEqual(key7, f'xyz_{dat}_{dattime}_{tpl}_{lst}_{obj}_Jon Doe_{point}_{set_value}_{MyEnum.one.value}')

    def test_keyable(self):
        def function_with_params(class_key):
            return 1

        key = build_function_key('{class_key}', function_with_params, User(1, 'Jon\n Doe'))
        self.assertEqual('User(id:1, name:Jon Doe)', key)

        key = build_function_key('{class_key}', function_with_params, User(2, 'Jon \rDoe'))
        self.assertEqual('User(id:2, name:Jon Doe)', key)

        key = build_function_key('{class_key}', function_with_params, User(3, 'Jon\n\r Doe'))
        self.assertEqual('User(id:3, name:Jon Doe)', key)

        def function_with_two_params(class_key, post):
            return 1

        key = build_function_key('{class_key}_{post}', function_with_two_params, User(3, 'Jon Doe'), 'developer')
        self.assertEqual('User(id:3, name:Jon Doe)_developer', key)

    def test_param_dict_func(self):
        def get_func_params_test_func(param_1, param_2, param_3=11, param_4=22):
            return 1

        dict1 = get_func_parameters_as_dict(get_func_params_test_func, *[1, 2], **{"param_3": 11, "param_4": 22})
        self.assertNotEqual(dict1, None)
        self.assertEqual(dict1['param_1'], 1)
        self.assertEqual(dict1['param_2'], 2)
        self.assertEqual(dict1['param_3'], 11)
        self.assertEqual(dict1['param_4'], 22)

        dict2 = get_func_parameters_as_dict(get_func_params_test_func, *[1, 2, 11, 22], **{})
        self.assertNotEqual(dict2, None)
        self.assertEqual(dict2['param_1'], 1)
        self.assertEqual(dict2['param_2'], 2)
        self.assertEqual(dict2['param_3'], 11)
        self.assertEqual(dict2['param_4'], 22)

        dict3 = get_func_parameters_as_dict(get_func_params_test_func, *[11, 22])
        self.assertNotEqual(dict3, None)
        self.assertEqual(dict3['param_1'], 11)
        self.assertEqual(dict3['param_2'], 22)
        self.assertEqual(dict3['param_3'], 11)
        self.assertEqual(dict3['param_4'], 22)

        dict4 = get_func_parameters_as_dict(get_func_params_test_func, None, None)
        self.assertNotEqual(dict4, None)
        self.assertEqual(dict4['param_1'], None)
        self.assertEqual(dict4['param_2'], None)
        self.assertEqual(dict4['param_3'], 11)
        self.assertEqual(dict4['param_4'], 22)

        dict5 = get_func_parameters_as_dict(get_func_params_test_func, None, None, None)
        self.assertNotEqual(dict5, None)
        self.assertEqual(dict5['param_1'], None)
        self.assertEqual(dict5['param_2'], None)
        self.assertEqual(dict5['param_3'], None)
        self.assertEqual(dict5['param_4'], 22)
        self.assertEqual(len(dict5), 4)

        dict6 = get_func_parameters_as_dict(get_func_params_test_func, *[1, 2, 3], **{})
        self.assertNotEqual(dict6, None)
        self.assertEqual(dict6['param_1'], 1)
        self.assertEqual(dict6['param_2'], 2)
        self.assertEqual(dict6['param_3'], 3)
        self.assertEqual(dict6['param_4'], 22)
        self.assertEqual(len(dict6), 4)

        dict7 = get_func_parameters_as_dict(get_func_params_test_func, *[1, 2], **{'param_3': 22})
        self.assertNotEqual(dict7, None)
        self.assertEqual(dict7['param_1'], 1)
        self.assertEqual(dict7['param_2'], 2)
        self.assertEqual(dict7['param_3'], 22)
        self.assertEqual(dict7['param_4'], 22)
        self.assertEqual(len(dict7), 4)

        dict8 = get_func_parameters_as_dict(get_func_params_test_func)
        self.assertNotEqual(dict8, None)
        self.assertEqual(len(dict8), 4)
        self.assertEqual(dict8['param_1'], None)
        self.assertEqual(dict8['param_2'], None)
        self.assertEqual(dict8['param_3'], 11)
        self.assertEqual(dict8['param_4'], 22)

    def test_param_index_func(self):
        def function_with_parameters(param_1, param_2, param_3, param_4=11, param_5=22):
            return 1

        index1 = get_func_parameter_index_by_name(function_with_parameters, "param_1")
        self.assertEqual(index1, 0)

        index2 = get_func_parameter_index_by_name(function_with_parameters, "param_2")
        self.assertEqual(index2, 1)

        index3 = get_func_parameter_index_by_name(function_with_parameters, "param_3")
        self.assertEqual(index3, 2)

        index4 = get_func_parameter_index_by_name(function_with_parameters, "param_4")
        self.assertEqual(index4, 3)

        index4 = get_func_parameter_index_by_name(function_with_parameters, "param_5")
        self.assertEqual(index4, 4)

        with self.assertRaises(Exception):
            get_func_parameter_index_by_name(function_with_parameters)

        with self.assertRaises(Exception):
            get_func_parameter_index_by_name(function_with_parameters, "param_46")
