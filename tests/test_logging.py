import datetime
import unittest
import logging

from core_lib.helpers.logging import Logging


class LogStream(object):
    def __init__(self):
        self.logs = ''

    def write(self, str):
        self.logs += str

    def flush(self):
        pass

    def __str__(self):
        return self.logs


class TestLogging(unittest.TestCase):

    def test_string_logger(self):
        string = "hello"

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message_params(string)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.self_hello"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message(string)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.TestLogging.logging_message"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_params(string)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.self_hello"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_classname(string)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.TestLogging.logging_classname"])

    def test_object_logger(self):
        dat = datetime.date(2022, 1, 1)
        obj = {
            'date': dat,
            'tuple': ("fruit", "apple"),
            'list': ["fruit", "apple"]
        }

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message_params(obj)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.self_{'date': datetime.date(2022, 1, 1), 'tuple': ('fruit', 'apple'), 'list': ['fruit', 'apple']}"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message(obj)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.TestLogging.logging_message"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_params(obj)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.self_{'date': datetime.date(2022, 1, 1), 'tuple': ('fruit', 'apple'), 'list': ['fruit', 'apple']}"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_classname(obj)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.TestLogging.logging_classname"])

    def test_tuple_logger(self):
        tpl = ("fruit", "apple")

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message_params(tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.self_('fruit', 'apple')"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message(tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.TestLogging.logging_message"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_params(tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.self_('fruit', 'apple')"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_classname(tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.TestLogging.logging_classname"])

    def test_list_logger(self):
        lst = ["fruit", "apple"]

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message_params(lst)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.self_['fruit', 'apple']"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message(lst)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.TestLogging.logging_message"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_params(lst)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.self_['fruit', 'apple']"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_classname(lst)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.TestLogging.logging_classname"])

    def test_multi_param_logger(self):
        lst = ["fruit", "apple"]
        tpl = ("fruit", "apple")

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message_multi_params(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.self_hello world_['fruit', 'apple']_('fruit', 'apple')"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_message_multi_params("hello world",lst,  tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.self_hello world_['fruit', 'apple']_('fruit', 'apple')"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_multi_params_message(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:log_for_test.TestLogging.logging_multi_params_message"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_multi_params(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.self_hello world_['fruit', 'apple']_('fruit', 'apple')"])

        with self.assertLogs('core_lib.helpers.logging', level='DEBUG') as cm:
            self.logging_multi_params_classname(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(cm.output, ["INFO:core_lib.helpers.logging:.TestLogging.logging_multi_params_classname"])

    @Logging(message="log_for_test", log_parameters=True)
    def logging_message_params(self, param):
        return param

    @Logging(message="log_for_test")
    def logging_message(self, param):
        return param

    @Logging(log_parameters=True)
    def logging_params(self, param):
        return param

    @Logging()
    def logging_classname(self, param):
        return param

    @Logging(message="log_for_test", log_parameters=True)
    def logging_message_multi_params(self, param_1: str, param_2: list, param_3: tuple):
        return "logged"

    @Logging(message="log_for_test")
    def logging_multi_params_message(self, param_1: str, param_2: list, param_3: tuple):
        return "logged"

    @Logging(log_parameters=True)
    def logging_multi_params(self, param_1: str, param_2: list, param_3: tuple):
        return "logged"

    @Logging()
    def logging_multi_params_classname(self, param_1: str, param_2: list, param_3: tuple):
        return "logged"
