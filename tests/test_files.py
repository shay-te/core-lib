import os
import unittest

from core_lib.helpers.files import compare_files_md5


class TestFiles(unittest.TestCase):
    def test_compare(self):
        image_file = os.path.join(os.path.dirname(__file__), 'test_data/koala.jpeg')
        other_file = os.path.join(os.path.dirname(__file__), 'test_files.py')
        self.assertTrue(compare_files_md5(image_file, image_file))
        self.assertTrue(compare_files_md5(other_file, other_file))
        self.assertFalse(compare_files_md5(other_file, image_file))
