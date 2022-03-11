import datetime
import logging
import unittest

from core_lib.helpers.func_utils import Keyable
from core_lib.helpers.logging import Logging


class User(Keyable):
    def __init__(self, u_name: str):
        self.u_name = u_name

    def key(self) -> str:
        return f'User(u_name:{self.u_name})'


class GetHugeData(Keyable):
    def __init__(self, source: str, data: dict):
        self.source = source
        self.data = data

    def key(self) -> str:
        return f'GetHugeData(source:{self.source}, data:{self.data[list(self.data)[0]]})'


class TestLogging(unittest.TestCase):
    string = 'hello world'
    dat = datetime.date(2022, 1, 1)
    obj = {'date': dat, 'tuple': ("fruit", "apple"), 'list': ["fruit", "apple"]}
    tpl = ('fruit', 'apple')
    lst = ['fruit', 'apple']

    def test_string_logger(self):
        with self.assertLogs('TestLogging.logging_message', level='ERROR') as cm:
            self.logging_message(self.string)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_message_with_params', level='ERROR') as cm:
            self.logging_message_with_params(self.string)
        self.assertEqual(cm.output, [f'ERROR:TestLogging.logging_message_with_params:test_parameter_{self.string}'])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(self.string)
        self.assertEqual(cm.output, ['INFO:TestLogging.logging_without_message:'])

    def test_object_logger(self):
        with self.assertLogs('TestLogging.logging_message', level='ERROR') as cm:
            self.logging_message(self.obj)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_message_with_params', level='ERROR') as cm:
            self.logging_message_with_params(self.obj)
        self.assertEqual(
            cm.output,
            [f'ERROR:TestLogging.logging_message_with_params:test_parameter_{self.obj}'],
        )

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(self.obj)
        self.assertEqual(
            cm.output,
            ['INFO:TestLogging.logging_without_message:'],
        )

    def test_tuple_logger(self):
        with self.assertLogs('TestLogging.logging_message', level='ERROR') as cm:
            self.logging_message(self.tpl)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_message_with_params', level='ERROR') as cm:
            self.logging_message_with_params(self.tpl)
        self.assertEqual(cm.output, [f'ERROR:TestLogging.logging_message_with_params:test_parameter_{self.tpl}'])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(self.tpl)
        self.assertEqual(cm.output, ['INFO:TestLogging.logging_without_message:'])

    def test_list_logger(self):
        with self.assertLogs('TestLogging.logging_message', level='ERROR') as cm:
            self.logging_message(self.lst)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_message_with_params', level='ERROR') as cm:
            self.logging_message_with_params(self.lst)
        self.assertEqual(cm.output, [f'ERROR:TestLogging.logging_message_with_params:test_parameter_{self.lst}'])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(self.lst)
        self.assertEqual(cm.output, ['INFO:TestLogging.logging_without_message:'])

    def test_multi_param_logger(self):

        with self.assertLogs('TestLogging.logging_multi_params_message', level='ERROR') as cm:
            self.logging_multi_params_message(param_1=self.string, param_2=self.lst, param_3=self.tpl)
        self.assertEqual(cm.output, ['ERROR:TestLogging.logging_multi_params_message:log_for_test'])

        with self.assertLogs('TestLogging.logging_multi_params_message_with_params', level='ERROR') as cm:
            self.logging_multi_params_message_with_params(param_1=self.string, param_2=self.lst, param_3=self.tpl)
        self.assertEqual(
            cm.output,
            [
                f'ERROR:TestLogging.logging_multi_params_message_with_params:test_parameter_{self.string}_{self.lst}_{self.tpl}'
            ],
        )

        with self.assertLogs('TestLogging.logging_multi_params_without_message', level='INFO') as cm:
            self.logging_multi_params_without_message(param_1=self.string, param_2=self.lst, param_3=self.tpl)
        self.assertEqual(cm.output, ['INFO:TestLogging.logging_multi_params_without_message:'])

    def test_keyable_logging(self):
        username = 'jon_doe'
        source = 'old_user_base'
        with self.assertLogs('TestLogging.logging_keyable', level='INFO') as cm:
            self.logging_keyable(User(username))
        self.assertEqual(cm.output, [f'ERROR:TestLogging.logging_keyable:test_keyable_User(u_name:{username})'])

        with self.assertLogs('TestLogging.logging_keyable', level='INFO') as cm:
            self.logging_keyable(GetHugeData(source, {'data': 'huge dict of data', 'more_data': 'some more huge data'}))
        self.assertEqual(
            cm.output,
            [f'ERROR:TestLogging.logging_keyable:test_keyable_GetHugeData(source:{source}, data:huge dict of data)'],
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
