"""Testing Module For Logging in and obtaining an access Token"""
import os
import pytest
import httpx

from libtick.tick_tick import TickTickClient


class TestClient:

    def test_good_login(self, client):
        """Tests login is valid in conftest.py"""
        assert client.access_token != ''

    def test_bad_login(self, client):
        """Tests invalid login"""
        user = 'not'
        passw = 'good'
        with pytest.raises(RuntimeError):
            test_client = TickTickClient(user, passw)

    def test_check_status_code(self, client):
        """Tests that a failed httpx request raises an exception"""
        url = client.BASE_URL + 'badurl'
        response = httpx.get(url, cookies=client.cookies)
        with pytest.raises(RuntimeError):
            client.check_status_code(response, 'Error')

    def test_not_logged_in(self, client):
        """Tests that an exception is raised when access_token is not alive"""
        original_token = client.access_token
        client.access_token = ''
        with pytest.raises(RuntimeError):
            client.delete_list('1234')
        client.access_token = original_token

    def test_initial_sync(self, client):
        response = client._initial_sync()
        assert response.status_code == 200

    def test_settings(self, client):
        response = client._settings()
        assert response.status_code == 200
        assert client.profile_id is not None
        assert client.time_zone != ''

