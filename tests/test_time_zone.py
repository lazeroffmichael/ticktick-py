"""Testing module for local timezone to UTC conversion"""

from datetime import datetime
from helpers.time_zone import convert_local_time_to_utc


class TestTimeConversions:
    def test_pacific_time(self):
        pst = datetime(2020, 12, 14, 1, 19, 0)
        expected_utc = datetime(2020, 12, 14, 9, 19, 0)
        assert convert_local_time_to_utc(pst, 'America/Los_Angeles') == expected_utc

    def test_pacific_time_2(self):
        pst = datetime(2020, 12, 14, 1, 19, 0)
        expected_utc = datetime(2020, 12, 14, 9, 19, 0)
        assert convert_local_time_to_utc(pst, 'US/Pacific') == expected_utc

    def test_pacific_time_midnight(self):
        pst = datetime(2020, 12, 14)
        expected_utc = datetime(2020, 12, 14, 8)
        assert convert_local_time_to_utc(pst, 'US/Pacific') == expected_utc

    def test_pacific_time_11_59(self):
        pst = datetime(2020, 12, 11, 23, 59)
        expected_utc = datetime(2020, 12, 12, 7, 59)
        assert convert_local_time_to_utc(pst, 'US/Pacific') == expected_utc

    def test_tokyo_time(self):
        tokyo = datetime(2020, 12, 14, 18, 38)
        expected_utc = datetime(2020, 12, 14, 9, 38)
        assert convert_local_time_to_utc(tokyo, 'Asia/Tokyo') == expected_utc
