"""
Integration tests for api.py
"""

import pytest
import httpx
import uuid

from ticktick.api import TickTickClient
from ticktick.oauth2 import OAuth2
from unittest.mock import patch


class TestInitMethod:

    def test_good_login(self, client):
        """
        Tests proper preparing of the session when initializing the object
        """
        assert client.access_token != ''
        assert client.cookies['t']
        assert client.time_zone
        assert client.profile_id
        assert client.inbox_id
        assert client.state

    def test_bad_login(self, client):
        """Tests invalid login"""
        user = str(uuid.uuid4())
        passw = str(uuid.uuid4())
        client_id = str(uuid.uuid4())
        with patch('ticktick.oauth2.OAuth2.get_access_token'):
            auth = OAuth2(client_id, client_id, client_id)
        with pytest.raises(Exception):
            TickTickClient(user, passw, auth)


def test_check_status_code(client):
    """Tests that a failed httpx request raises an exception"""
    url = client.BASE_URL + str(uuid.uuid4())
    response = httpx.get(url, cookies=client.cookies)
    with pytest.raises(RuntimeError):
        client.check_status_code(response, 'Error')
