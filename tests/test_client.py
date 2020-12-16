"""Testing Module For Logging in and obtaining an access Token"""
import os
import pytest
import httpx

from libtick.tick_tick import TickTickClient
from datetime import datetime


class TestClient:

    def test_good_login(self, client):
        assert client.access_token != ''

    def test_bad_login(self, client):
        user = 'not'
        passw = 'good'
        with pytest.raises(ValueError):
            test_client = TickTickClient(user, passw)

    def test_check_status_code(self, client):
        url = client.BASE_URL + 'badurl'
        response = httpx.get(url, cookies=client.cookies)
        with pytest.raises(ValueError):
            client.check_status_code(response, 'Error')

    def test_not_logged_in(self, client):
        user = os.getenv('TICKTICK_USER')
        passw = os.getenv('TICKTICK_PASS')
        new_client = TickTickClient(user, passw)
        new_client.access_token = ''
        with pytest.raises(ValueError):
            new_client.delete_list('1234')

    def test_invalid_time_zone_get_summary(self,client):
        start = datetime(2020, 12, 14)
        end = datetime(2020, 12, 14)
        tz = 'THIS AINT IT CHIEF'
        tasks = client.get_summary(tz, start, end)

    def test_get_summary_single_day_good_return(self, client):
        start = datetime(2020, 12, 14)
        end = datetime(2020, 12, 14)
        tz = 'US/Pacific'
        tasks = client.get_summary(tz, start, end)
        assert tasks != []

    def test_get_summary_multi_day_good_return(self, client):
        start = datetime(2020, 12, 10)
        end = datetime(2020, 12, 14)
        tz = 'US/Pacific'
        tasks = client.get_summary(tz, start, end)
        assert tasks != []

    def test_get_summary_bad_start_and_end(self, client):
        start = datetime(2020, 11, 14)
        end = datetime(2020, 11, 10)
        tz = 'US/Pacific'
        tasks = client.get_summary(tz, start, end)
        assert tasks == []
