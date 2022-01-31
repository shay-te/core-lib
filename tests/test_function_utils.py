import unittest

from core_lib.helpers.func_utils import build_value_by_func_parameters, get_func_parameters_as_dict, \
    get_func_parameter_index_by_name, get_calling_module


class TestFunctionUtils(unittest.TestCase):

    def test_cache_generates_key(self):
        def boo(param_1, param_2):
            return 1

        key1 = build_value_by_func_parameters('asdfghjklzxcvbnm', boo, *[1234, 12345134], **{})
        self.assertNotEqual(key1, None)
        self.assertEqual(key1, 'asdfghjklzxcvbnm')

        key2 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', boo, *[11, 22], **{})
        self.assertNotEqual(key2, None)
        self.assertEqual(key2, 'xyz_11_22')

        key3 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', boo, *[11], **{})
        self.assertNotEqual(key3, None)
        self.assertEqual(key3, 'xyz_11_param_2')

        key4 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', boo, *[], **{'param_2': 'pp2'})
        self.assertNotEqual(key4, None)
        self.assertEqual(key4, 'xyz_param_1_pp2')

        key5 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', boo, 1, 2)
        self.assertNotEqual(key5, None)
        self.assertEqual(key5, 'xyz_1_2')

        key6 = build_value_by_func_parameters('xyz_{param_1}_{param_2}', boo, None, None)
        self.assertNotEqual(key6, None)
        self.assertEqual(key6, 'xyz_None_None')

    def test_func_param_to_dict(self):
        def boo(param_1, param_2):
            return 1

        dict1 = get_func_parameters_as_dict(boo, 1, 2)
        self.assertNotEqual(dict1, None)
        self.assertEqual(dict1['param_1'], 1)
        self.assertEqual(dict1['param_2'], 2)

        dict2 = get_func_parameters_as_dict(boo, *[1, 2], **{})
        self.assertNotEqual(dict2, None)
        self.assertEqual(dict2['param_1'], 1)
        self.assertEqual(dict2['param_2'], 2)

        dict3 = get_func_parameters_as_dict(boo, *[11], **{'param_2': 22})
        self.assertNotEqual(dict3, None)
        self.assertEqual(dict3['param_1'], 11)
        self.assertEqual(dict3['param_2'], 22)

        dict4 = get_func_parameters_as_dict(boo, None, None)
        self.assertNotEqual(dict4, None)
        self.assertEqual(dict4['param_1'], None)
        self.assertEqual(dict4['param_2'], None)

    def test_func_param_index_by_name(self):
        def boo(param_1, param_2, param_3):
            return 1

        def foo(test_param):
            return 1

        index1 = get_func_parameter_index_by_name(boo, "param_1")
        self.assertNotEqual(index1, None)
        self.assertEqual(index1, 0)

        index2 = get_func_parameter_index_by_name(boo, "param_2")
        self.assertNotEqual(index2, None)
        self.assertEqual(index2, 1)

        index3 = get_func_parameter_index_by_name(boo, "param_3")
        self.assertNotEqual(index3, None)
        self.assertEqual(index3, 2)

        index4 = get_func_parameter_index_by_name(foo, "test_param")
        self.assertNotEqual(index4, None)
        self.assertEqual(index4, 0)

    def test_get_calling_module(self):
        self.assertNotEqual(get_calling_module(stack_depth=1), None)
        self.assertEqual(get_calling_module(stack_depth=1), "test_function_utils")
