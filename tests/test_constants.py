import unittest

from core_lib.helpers.constants import HttpHeaders


class TestConstants(unittest.TestCase):
    def test_accept_ranges_keeps_misspelled_alias(self):
        self.assertEqual('Accept-Ranges', HttpHeaders.ACCEPT_RANGES.value)
        self.assertIs(HttpHeaders.ACCEPT_RANGES, HttpHeaders.ACCEPT_RANGERS)
        self.assertIs(HttpHeaders.ACCEPT_RANGES, HttpHeaders('Accept-Ranges'))
        self.assertEqual('ACCEPT_RANGES', HttpHeaders.ACCEPT_RANGERS.name)
