import unittest

from core_lib.helpers.instance_under_stack import InstanceUnderStack

instance_under_stack = InstanceUnderStack(stack_start_index=3)


def func_5():
    return instance_under_stack.store('')


def func_4():
    return func_5()


def func_3():
    return func_4()


def func_2():
    return func_3()


def func_1():
    return func_2()


class TestInstanceUnderStack(unittest.TestCase):

    stack_func_5 = None

    def test_path(self):
        stack_path1 = func_1()
        stack_path2 = func_1()
        self.assertEqual(stack_path1, stack_path2)

    def test_multi_threaded(self):
        pass

    def test_multi_process(self):
        pass

    def test_multi_threaded_and_multi_process(self):
        # validate that no colusion and process id + thread id get different id
        # dose threading.get_native_id() acualy works?
        pass
