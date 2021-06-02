"""Testing module for TickTickClient class"""
import pytest
import httpx
import uuid
import os

from ticktick.api import TickTickClient


# TODO: refactor api tests


def test_good_login(client):
    """Tests login is valid in conftest.py"""
    assert client.access_token != ''


def test_bad_login(client):
    """Tests invalid login"""
    user = str(uuid.uuid4())
    passw = str(uuid.uuid4())
    with pytest.raises(RuntimeError):
        TickTickClient(user, passw)


def test_check_status_code(client):
    """Tests that a failed httpx request raises an exception"""
    url = client.BASE_URL + str(uuid.uuid4())
    response = httpx.get(url, cookies=client.cookies)
    with pytest.raises(RuntimeError):
        client.check_status_code(response, 'Error')


def test_not_logged_in(client):
    """Tests that an exception is raised when access_token is not alive"""
    original_token = client.access_token
    client.access_token = ''
    with pytest.raises(RuntimeError):
        client.sync()
    client.access_token = original_token


def test_settings(client):
    """Tests _settings() retrieves values"""
    client._settings()
    assert client.profile_id is not None
    assert client.time_zone != ''

