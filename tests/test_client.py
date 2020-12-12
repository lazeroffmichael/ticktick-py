"""Testing Module For Logging in and obtaining an access Token"""
import os

import pytest

from libtick.client import TickTickClient


class TestClient:
    def test_login_return(self):
        user = os.getenv('TICKTICK_USER')
        passw = os.getenv('TICKTICK_PASS')
        client = TickTickClient(user, passw)
        assert client.access_token != ''

    def test_bad_login(self):
        user = 'not'
        passw = 'good'
        with pytest.raises(ValueError):
            client = TickTickClient(user, passw)
