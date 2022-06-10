import os
import re
import unittest

from core_lib.helpers.files import get_file_md5


class TestFiles(unittest.TestCase):
    def test_get_file_md5(self):
        regex = r"([a-fA-F\d]{32})"
        image_file = os.path.join(os.path.dirname(__file__), 'test_data/koala.jpeg')
        other_file = os.path.join(os.path.dirname(__file__), 'test_files.py')
        self.assertIsNotNone(re.match(regex, get_file_md5(other_file)))
        self.assertIsNotNone(re.match(regex, get_file_md5(image_file)))
