import unittest

from core_lib.job.job_decorations import parse_input_time_string


class TestTimeParsing(unittest.TestCase):

    def test_1_expressions(self):
        self.assertEqual(parse_input_time_string('10s'), (10, 's'))
        self.assertEqual(parse_input_time_string('19m'), (19, 'm'))
        self.assertEqual(parse_input_time_string('49h'), (49, 'h'))
        self.assertEqual(parse_input_time_string('119h'), (119, 'h'))
        self.assertEqual(parse_input_time_string('111239w'), (111239, 'w'))

        self.assertRaises(ValueError, parse_input_time_string, '219.1m')
        self.assertRaises(ValueError, parse_input_time_string, '')
        self.assertRaises(ValueError, parse_input_time_string, None)
        self.assertRaises(ValueError, parse_input_time_string, 123)

