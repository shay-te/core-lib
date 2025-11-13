import unittest

from core_lib.middleware.middleware import Middleware
from core_lib.middleware.middleware_chain import MiddlewareChain

global_list = []

TEST_1 = 'test_1'
TEST_2 = 'test_2'

class TestMiddleware1(Middleware):
    def handle(self, context):
        global global_list
        global_list.append(TEST_1)


class TestMiddleware2(Middleware):
    def handle(self, context):
        global global_list
        global_list.append(TEST_2)


class TestMiddlewareChain(unittest.TestCase):

    def setUp(self):
        global global_list
        global_list = []
        self.chain = MiddlewareChain()

    def test_middlewares_are_executed(self):
        self.chain.add(TestMiddleware1())
        self.chain.add(TestMiddleware2())

        self.chain.execute(context={"exc": Exception("test"), "func": lambda: None})
        self.assertEqual(len(global_list), 2)
        self.assertEqual(global_list[0], TEST_1)
        self.assertEqual(global_list[1], TEST_2)

    def test_clear_removes_all_middlewares(self):
        self.chain.add(TestMiddleware1())
        self.chain.add(TestMiddleware2())
        self.chain.clear()

        self.chain.execute(context={})
        self.assertEqual(len(global_list), 0)

    def test_remove_specific_middleware(self):
        mw1 = TestMiddleware1()
        mw2 = TestMiddleware2()
        self.chain.add(mw1)
        self.chain.add(mw2)

        self.chain.remove(mw1)
        self.chain.execute(context={})

        self.assertEqual(len(global_list), 1)
        self.assertEqual(global_list[0], TEST_2)