"""Testing module for local timezone to UTC conversion"""

from datetime import datetime
from ticktick.helpers.time_methods import convert_local_time_to_utc, convert_date_to_tick_tick_format


def test_pacific_time():
    pst = datetime(2020, 12, 14, 1, 19, 0)
    expected_utc = datetime(2020, 12, 14, 9, 19, 0)
    assert convert_local_time_to_utc(pst, 'America/Los_Angeles') == expected_utc


def test_pacific_time_2():
    pst = datetime(2020, 12, 14, 1, 19, 0)
    expected_utc = datetime(2020, 12, 14, 9, 19, 0)
    assert convert_local_time_to_utc(pst, 'US/Pacific') == expected_utc


def test_pacific_time_midnight():
    pst = datetime(2020, 12, 14)
    expected_utc = datetime(2020, 12, 14, 8)
    assert convert_local_time_to_utc(pst, 'US/Pacific') == expected_utc


def test_pacific_time_11_59():
    pst = datetime(2020, 12, 11, 23, 59)
    expected_utc = datetime(2020, 12, 12, 7, 59)
    assert convert_local_time_to_utc(pst, 'US/Pacific') == expected_utc


def test_tokyo_time():
    tokyo = datetime(2020, 12, 14, 18, 38)
    expected_utc = datetime(2020, 12, 14, 9, 38)
    assert convert_local_time_to_utc(tokyo, 'Asia/Tokyo') == expected_utc


def test_convert_iso_to_tick_tick():
    date = datetime(2022, 12, 31, 14, 30, 45)
    expected = '2022-12-31T22:30:45+0000'
    assert convert_date_to_tick_tick_format(date, 'US/Pacific') == expected


def test_convert_iso_to_tick_tick_2():
    date = datetime(2022, 12, 31)
    expected = '2022-12-31T08:00:00+0000'
    assert convert_date_to_tick_tick_format(date, 'US/Pacific') == expected

