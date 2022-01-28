import unittest

from core_lib.helpers.func_utils import build_value_by_func_parameters


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
