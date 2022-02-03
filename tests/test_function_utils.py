import datetime
import unittest

from core_lib.helpers.func_utils import build_value_by_func_parameters, get_func_parameters_as_dict, \
    get_func_parameter_index_by_name, get_calling_module, reset_datetime


class TestFunctionUtils(unittest.TestCase):

    def test_cache_generates_key(self):
        def returns_1(param_1, param_2, param_3=11, param_4=22):
            return 1

        key1 = build_value_by_func_parameters('asdfghjklzxcvbnm', returns_1, *[1234, 12345134], **{})
        self.assertNotEqual(key1, None)
        self.assertEqual(key1, 'asdfghjklzxcvbnm')

        key2 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', returns_1, *[11, 22], **{})
        self.assertNotEqual(key2, None)
        self.assertEqual(key2, 'xyz_11_22')

        key3 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', returns_1, *[11], **{})
        self.assertNotEqual(key3, None)
        self.assertEqual(key3, 'xyz_11_param_2')

        key4 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', returns_1, *[], **{'param_2': 'pp2'})
        self.assertNotEqual(key4, None)
        self.assertEqual(key4, 'xyz_param_1_pp2')

        key5 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', returns_1, 1, 2)
        self.assertNotEqual(key5, None)
        self.assertEqual(key5, 'xyz_1_2')

        key6 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', returns_1, None, None)
        self.assertNotEqual(key6, None)
        self.assertEqual(key6, 'xyz_None_None')

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
        self.assertEqual(dict8['param_1'], 'param_1')
        self.assertEqual(dict8['param_2'], 'param_2')
        self.assertEqual(dict8['param_3'], 11)
        self.assertEqual(dict8['param_4'], 22)

    def test_param_index_func(self):
        def returns_1(param_1, param_2, param_3, param_4=11, param_5=22):
            return 1

        index1 = get_func_parameter_index_by_name(returns_1, "param_1")
        self.assertEqual(index1, 0)

        index2 = get_func_parameter_index_by_name(returns_1, "param_2")
        self.assertEqual(index2, 1)

        index3 = get_func_parameter_index_by_name(returns_1, "param_3")
        self.assertEqual(index3, 2)

        index4 = get_func_parameter_index_by_name(returns_1, "param_4")
        self.assertEqual(index4, 3)

        index4 = get_func_parameter_index_by_name(returns_1, "param_5")
        self.assertEqual(index4, 4)

        with self.assertRaises(Exception):
            get_func_parameter_index_by_name(returns_1)

        with self.assertRaises(Exception):
            get_func_parameter_index_by_name(returns_1, "param_46")

    def test_get_calling_module(self):
        self.assertNotEqual(get_calling_module(stack_depth=1), None)
        self.assertEqual(get_calling_module(stack_depth=1), "tests.test_function_utils")

    def test_reset_date(self):
        dattime = datetime.datetime.utcnow()
        self.assertEqual(reset_datetime(dattime), dattime.replace(hour=0, minute=0, second=0, microsecond=0))
        self.assertEqual(reset_datetime(date=dattime), dattime.replace(hour=0, minute=0, second=0, microsecond=0))
