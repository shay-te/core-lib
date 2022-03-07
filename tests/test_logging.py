import datetime
import logging
import unittest

from core_lib.helpers.func_utils import Keyable
from core_lib.helpers.logging import Logging


class User(Keyable):
    def __init__(self, u_name, password):
        self.u_name = u_name
        self.password = password

    def key(self) -> str:
        return f'User(u_name:{self.u_name}, password:{type(self.password).__name__})'


class GetHugeData(Keyable):
    def __init__(self, source, data):
        self.source = source
        self.data = data

    def key(self) -> str:
        return f'GetHugeData(source:{self.source}, data:{type(self.data).__name__})'


class TestLogging(unittest.TestCase):
    def test_string_logger(self):
        string = 'hello'

        with self.assertLogs('TestLogging.logging_message', level='ERROR') as cm:
            self.logging_message(string)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_message_with_params', level='ERROR') as cm:
            self.logging_message_with_params(string)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message_with_params:test_parameter_hello'])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(string)
        self.assertEqual(cm.output, ['INFO:TestLogging.logging_without_message:'])

    def test_object_logger(self):
        dat = datetime.date(2022, 1, 1)
        obj = {'date': dat, 'tuple': ("fruit", "apple"), 'list': ["fruit", "apple"]}

        with self.assertLogs('TestLogging.logging_message', level='ERROR') as cm:
            self.logging_message(obj)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_message_with_params', level='ERROR') as cm:
            self.logging_message_with_params(obj)
        self.assertEqual(
            cm.output,
            [f'ERROR:TestLogging.logging_message_with_params:test_parameter_{obj}'],
        )

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(obj)
        self.assertEqual(
            cm.output,
            ['INFO:TestLogging.logging_without_message:'],
        )

    def test_tuple_logger(self):
        tpl = ('fruit', 'apple')

        with self.assertLogs('TestLogging.logging_message', level='ERROR') as cm:
            self.logging_message(tpl)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_message_with_params', level='ERROR') as cm:
            self.logging_message_with_params(tpl)
        self.assertEqual(cm.output, [f'ERROR:TestLogging.logging_message_with_params:test_parameter_{tpl}'])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(tpl)
        self.assertEqual(cm.output, ['INFO:TestLogging.logging_without_message:'])

    def test_list_logger(self):
        lst = ['fruit', 'apple']

        with self.assertLogs('TestLogging.logging_message', level='ERROR') as cm:
            self.logging_message(lst)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_message_with_params', level='ERROR') as cm:
            self.logging_message_with_params(lst)
        self.assertEqual(cm.output, [f'ERROR:TestLogging.logging_message_with_params:test_parameter_{lst}'])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(lst)
        self.assertEqual(cm.output, ['INFO:TestLogging.logging_without_message:'])

    def test_multi_param_logger(self):
        lst = ['fruit', 'apple']
        tpl = ('fruit', 'apple')

        with self.assertLogs('TestLogging.logging_multi_params_message', level='ERROR') as cm:
            self.logging_multi_params_message(param_1='hello world', param_2=lst, param_3=tpl)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_multi_params_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_multi_params_message_with_params', level='ERROR') as cm:
            self.logging_multi_params_message_with_params(param_1='hello world', param_2=lst, param_3=tpl)
        self.assertEqual(
            cm.output,
            [f'ERROR:TestLogging.logging_multi_params_message_with_params:test_parameter_hello world_{lst}_{tpl}'],
        )

        with self.assertLogs('TestLogging.logging_multi_params_without_message', level='INFO') as cm:
            self.logging_multi_params_without_message(param_1='hello world', param_2=lst, param_3=tpl)
        self.assertEqual(cm.output, ['INFO:TestLogging.logging_multi_params_without_message:'])

    def test_keyable_logging(self):
        with self.assertLogs('TestLogging.logging_keyable', level='INFO') as cm:
            self.logging_keyable(User('jon_doe', 'password@12345'))
        self.assertEqual(
            cm.output, ['ERROR:TestLogging.logging_keyable:test_keyable_User(u_name:jon_doe, password:str)']
        )

        with self.assertLogs('TestLogging.logging_keyable', level='INFO') as cm:
            self.logging_keyable(GetHugeData('old_user_base', {'data': 'huge dict of data'}))
        self.assertEqual(
            cm.output, ['ERROR:TestLogging.logging_keyable:test_keyable_GetHugeData(source:old_user_base, data:dict)']
        )

    @Logging(message='log_for_test', level=logging.ERROR)
    def logging_message(self, param):
        return param

    @Logging(message='test_parameter_{param}', level=logging.ERROR)
    def logging_message_with_params(self, param):
        return param

    @Logging()
    def logging_without_message(self, param):
        return param

    @Logging(message='log_for_test', level=logging.ERROR)
    def logging_multi_params_message(self, param_1: str = '', param_2: list = [], param_3: tuple = ()):
        return 'logged'

    @Logging(message='test_parameter_{param_1}_{param_2}_{param_3}', level=logging.ERROR)
    def logging_multi_params_message_with_params(self, param_1: str = '', param_2: list = [], param_3: tuple = ()):
        return 'logged'

    @Logging()
    def logging_multi_params_without_message(self, param_1: str = '', param_2: list = [], param_3: tuple = ()):
        return 'logged'

    @Logging(message='test_keyable_{keyable_class}', level=logging.ERROR)
    def logging_keyable(self, keyable_class):
        return 'logged'
