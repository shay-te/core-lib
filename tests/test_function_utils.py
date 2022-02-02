import unittest

from core_lib.helpers.func_utils import build_value_by_func_parameters, get_func_parameters_as_dict, \
    get_func_parameter_index_by_name


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

    def test_param_dict_func(self):
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

        dict5 = get_func_parameters_as_dict(boo, None, None, None)
        self.assertNotEqual(dict5, None)
        self.assertEqual(dict5['param_1'], None)
        self.assertEqual(dict5['param_2'], None)
        self.assertEqual(len(dict5), 2)

        dict6 = get_func_parameters_as_dict(boo, *[1, 2, 3], **{})
        self.assertNotEqual(dict6, None)
        self.assertEqual(dict6['param_1'], 1)
        self.assertEqual(dict6['param_2'], 2)
        self.assertEqual(len(dict6), 2)

        dict7 = get_func_parameters_as_dict(boo, *[1, 2], **{'param_2': 22})
        self.assertNotEqual(dict7, None)
        self.assertEqual(dict7['param_1'], 1)
        self.assertEqual(dict7['param_2'], 2)
        self.assertEqual(len(dict7), 2)

        dict8 = get_func_parameters_as_dict(boo)
        self.assertNotEqual(dict8, None)
        self.assertEqual(len(dict8), 0)

    def test_param_index_func(self):

        def boo(param_1, param_2, param_3):
            return 1

        index1 = get_func_parameter_index_by_name(boo, "param_1")
        self.assertEqual(index1, 0)

        index2 = get_func_parameter_index_by_name(boo, "param_2")
        self.assertEqual(index2, 1)

        index3 = get_func_parameter_index_by_name(boo, "param_3")
        self.assertEqual(index3, 2)

        with self.assertRaises(Exception):
            get_func_parameter_index_by_name(boo)

        with self.assertRaises(Exception):
            get_func_parameter_index_by_name(boo, "param_4")

