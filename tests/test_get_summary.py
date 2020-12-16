import pytest

from datetime import datetime


class TestGetSummary:

    def test_invalid_time_zone_get_summary(self, client):
        """Tests that an exception is raised if an invalid time zone is passed to get_summary"""
        start = datetime(2020, 12, 14)
        end = datetime(2020, 12, 14)
        tz = 'THIS AINT IT CHIEF'
        with pytest.raises(ValueError):
            client.get_summary(tz, start, end)

    def test_get_summary_single_day_good_return(self, client):
        """Tests that on good inputs for a single day get_summary values are returned"""
        start = datetime(2020, 12, 14)
        tz = 'US/Pacific'
        tasks = client.get_summary(tz, start)
        assert tasks[0] != ''

    def test_get_summary_single_day_full_day_false(self, client):
        """Tests that input still works for a single day even when full_day is false"""
        start = datetime(2020, 12, 14, 8)
        tz = 'US/Pacific'
        tasks = client.get_summary(tz, start, full_day=False)
        assert tasks[0] != ''

    def test_get_summary_multi_day_full_good_return(self, client):
        """Tests that a multi day range returns a value"""
        start = datetime(2020, 12, 10)
        end = datetime(2020, 12, 14)
        tz = 'US/Pacific'
        tasks = client.get_summary(tz, start, end)
        assert tasks[0] != ''

    def test_get_summary_multi_day_not_full_day_good_return(self, client):
        """Tests that multi day with full_day=false returns a value"""
        start = datetime(2020, 12, 10, 12, 5, 6)
        end = datetime(2020, 12, 14, 12, 5, 6)
        tz = 'US/Pacific'
        tasks = client.get_summary(tz, start, end, full_day=False)
        assert tasks[0] != ''

    def test_get_summary_multi_day_good_return(self, client):
        """Tests that multi day works normally"""
        start = datetime(2020, 12, 10)
        end = datetime(2020, 12, 14)
        tz = 'US/Pacific'
        tasks = client.get_summary(tz, start, end)
        assert tasks[0] != ''

    def test_get_summary_bad_start_and_end(self, client):
        start = datetime(2020, 11, 14)
        end = datetime(2020, 11, 10)
        tz = 'US/Pacific'
        with pytest.raises(ValueError):
            client.get_summary(tz, start, end)
