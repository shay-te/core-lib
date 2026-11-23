"""A string `expire` given to `@Cache` is parsed to exactly the time written, whatever part of a second the clock
shows when the function is decorated. The real clock is used: freezegun mixes local time and UTC in `parse`."""
import time
import unittest
from datetime import timedelta

from core_lib.cache.cache_decorator import Cache

WRITTEN_EXPIRES = {
    '1 second': timedelta(seconds=1),
    '2 seconds': timedelta(seconds=2),
    '1 minute': timedelta(minutes=1),
    '1 hour': timedelta(hours=1),
    '1 day': timedelta(days=1),
    '1 week': timedelta(weeks=1),
}
PARTS_OF_A_SECOND = (0.05, 0.3, 0.55, 0.7, 0.9)  # where the clock is, inside its second, at decoration time
WINDOW = 0.05


def _wait_until_the_clock_shows(part_of_a_second: float):
    while not part_of_a_second <= time.time() % 1 < part_of_a_second + WINDOW:
        time.sleep(0.002)


class TestCacheStringExpire(unittest.TestCase):

    def test_a_string_expire_is_exactly_the_time_written_at_any_part_of_a_second(self):
        for part_of_a_second in PARTS_OF_A_SECOND:
            _wait_until_the_clock_shows(part_of_a_second)
            parsed = {text: Cache(expire=text).expire for text in WRITTEN_EXPIRES}
            for text, expected in WRITTEN_EXPIRES.items():
                with self.subTest(text=text, part_of_a_second=part_of_a_second):
                    self.assertEqual(expected, parsed[text])

    def test_a_string_expire_that_is_not_a_time_raises_at_decoration(self):
        with self.assertRaises(ValueError):
            Cache(expire='not a time')
