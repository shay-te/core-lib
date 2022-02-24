import datetime
import unittest

from core_lib.helpers.logging import Logging


class TestLogging(unittest.TestCase):
    def test_string_logger(self):
        string = "hello"

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params(string)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_params:log_for_test.hello"])

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params(None)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_params:log_for_test.!EparamE!"])

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params("")
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_params:log_for_test.!EparamE!"])

        with self.assertLogs('TestLogging.logging_message', level='INFO') as cm:
            self.logging_message(string)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message:log_for_test."])

        with self.assertLogs('TestLogging.logging_params', level='INFO') as cm:
            self.logging_params(string)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_params:.hello"])

    def test_object_logger(self):
        dat = datetime.date(2022, 1, 1)
        obj = {'date': dat, 'tuple': ("fruit", "apple"), 'list': ["fruit", "apple"]}

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params(obj)
        self.assertEqual(
            cm.output,
            [
                "INFO:TestLogging.logging_message_params:log_for_test.{'date': datetime.date(2022, 1, 1), 'tuple': ('fruit', 'apple'), 'list': ['fruit', 'apple']}"
            ],
        )

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params({})
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_params:log_for_test.!EparamE!"])

        with self.assertLogs('TestLogging.logging_message', level='INFO') as cm:
            self.logging_message(obj)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message:log_for_test."])

        with self.assertLogs('TestLogging.logging_params', level='INFO') as cm:
            self.logging_params(obj)
        self.assertEqual(
            cm.output,
            [
                "INFO:TestLogging.logging_params:.{'date': datetime.date(2022, 1, 1), 'tuple': ('fruit', 'apple'), 'list': ['fruit', 'apple']}"
            ],
        )

    def test_tuple_logger(self):
        tpl = ("fruit", "apple")

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params(tpl)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_params:log_for_test.('fruit', 'apple')"])

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params(())
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_params:log_for_test.!EparamE!"])

        with self.assertLogs('TestLogging.logging_message', level='INFO') as cm:
            self.logging_message(tpl)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message:log_for_test."])

        with self.assertLogs('TestLogging.logging_params', level='INFO') as cm:
            self.logging_params(tpl)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_params:.('fruit', 'apple')"])

    def test_list_logger(self):
        lst = ["fruit", "apple"]

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params(lst)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_params:log_for_test.['fruit', 'apple']"])

        with self.assertLogs('TestLogging.logging_message_params', level='INFO') as cm:
            self.logging_message_params([])
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_params:log_for_test.!EparamE!"])

        with self.assertLogs('TestLogging.logging_message', level='INFO') as cm:
            self.logging_message(lst)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message:log_for_test."])

        with self.assertLogs('TestLogging.logging_params', level='INFO') as cm:
            self.logging_params(lst)
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_params:.['fruit', 'apple']"])

    def test_multi_param_logger(self):
        lst = ["fruit", "apple"]
        tpl = ("fruit", "apple")

        with self.assertLogs('TestLogging.logging_message_multi_params', level='INFO') as cm:
            self.logging_message_multi_params(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(
            cm.output,
            [
                "INFO:TestLogging.logging_message_multi_params:log_for_test.hello world_['fruit', 'apple']_('fruit', 'apple')"
            ],
        )

        with self.assertLogs('TestLogging.logging_message_multi_params', level='INFO') as cm:
            self.logging_message_multi_params(param_1="", param_2=[], param_3=())
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_multi_params:log_for_test.!Eparam_1E!_!Eparam_2E!_!Eparam_3E!"])

        with self.assertLogs('TestLogging.logging_message_multi_params', level='INFO') as cm:
            self.logging_message_multi_params()
        self.assertEqual(cm.output, ["INFO:TestLogging.logging_message_multi_params:log_for_test.!Eparam_1E!_!Eparam_2E!_!Eparam_3E!"])

        with self.assertLogs('TestLogging.logging_message_multi_params', level='INFO') as cm:
            self.logging_message_multi_params("hello world", lst, tpl)
        self.assertEqual(
            cm.output, ["INFO:TestLogging.logging_message_multi_params:log_for_test.hello world_['fruit', 'apple']_('fruit', 'apple')"]
        )

        with self.assertLogs('TestLogging.logging_multi_params_message', level='INFO') as cm:
            self.logging_multi_params_message(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(
            cm.output, ["INFO:TestLogging.logging_multi_params_message:log_for_test."]
        )

        with self.assertLogs('TestLogging.logging_multi_params', level='INFO') as cm:
            self.logging_multi_params(param_1="hello world", param_2=lst, param_3=tpl)
        self.assertEqual(
            cm.output, ["INFO:TestLogging.logging_multi_params:.hello world_['fruit', 'apple']_('fruit', 'apple')"]
        )

    @Logging(message="log_for_test", log_parameters=True)
    def logging_message_params(self, param):
        return param

    @Logging(message="log_for_test")
    def logging_message(self, param):
        return param

    @Logging(log_parameters=True)
    def logging_params(self, param):
        return param

    @Logging(message="log_for_test", log_parameters=True)
    def logging_message_multi_params(self, param_1: str = "", param_2: list = [], param_3: tuple = ()):
        return "logged"

    @Logging(message="log_for_test")
    def logging_multi_params_message(self, param_1: str = "", param_2: list = [], param_3: tuple = ()):
        return "logged"

    @Logging(log_parameters=True)
    def logging_multi_params(self, param_1: str = "", param_2: list = [], param_3: tuple = ()):
        return "logged"
