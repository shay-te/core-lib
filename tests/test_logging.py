import datetime
import unittest

from core_lib.helpers.logging import Logging


class TestLogging(unittest.TestCase):
    def test_string_logger(self):
        string = "hello"

        with self.assertLogs('TestLogging.logging_message', level='INFO') as cm:
            self.logging_message(string)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message:log_for_test"])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(string)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_without_message:"])

    def test_object_logger(self):
        dat = datetime.date(2022, 1, 1)
        obj = {'date': dat, 'tuple': ("fruit", "apple"), 'list': ["fruit", "apple"]}

        with self.assertLogs('TestLogging.logging_message', level='INFO') as cm:
            self.logging_message(obj)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message:log_for_test"])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(obj)
        self.assertEqual(
            cm.output,
            ["INFO:TestLogging.logging_without_message:"],
        )

    def test_tuple_logger(self):
        tpl = ("fruit", "apple")

        with self.assertLogs('TestLogging.logging_message', level='INFO') as cm:
            self.logging_message(tpl)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message:log_for_test"])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(tpl)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_without_message:"])

    def test_list_logger(self):
        lst = ["fruit", "apple"]

        with self.assertLogs('TestLogging.logging_message', level='INFO') as cm:
            self.logging_message(lst)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message:log_for_test"])

        with self.assertLogs('TestLogging.logging_without_message', level='INFO') as cm:
            self.logging_without_message(lst)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_without_message:"])

    def test_multi_param_logger(self):
        lst = ["fruit", "apple"]
        tpl = ("fruit", "apple")

        with self.assertLogs('TestLogging.logging_multi_params_message', level='INFO') as cm:
            self.logging_multi_params_message(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_multi_params_message:log_for_test"])

        with self.assertLogs('TestLogging.logging_multi_params_without_message', level='INFO') as cm:
            self.logging_multi_params_without_message(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_multi_params_without_message:"])

    @Logging(message="log_for_test")
    def logging_message(self, param):
        return param

    @Logging()
    def logging_without_message(self, param):
        return param

    @Logging(message="log_for_test")
    def logging_multi_params_message(self, param_1: str = "", param_2: list = [], param_3: tuple = ()):
        return "logged"

    @Logging()
    def logging_multi_params_without_message(self, param_1: str = "", param_2: list = [], param_3: tuple = ()):
        return "logged"
