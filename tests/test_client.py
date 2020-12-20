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
            client._sync()
        client.access_token = original_token

    def test_initial_sync(self, client):
        response = client._sync()
        assert client.state['inbox_id'] != ''

    def test_settings(self, client):
        response = client._settings()
        assert client.profile_id is not None
        assert client.time_zone != ''

    def test_get_id(self, client):
        list_name = 'jfkldjfkdjfa;kjfkljalkf'
        response = client.list_create(list_name)
        found_id = client.get_id(name=list_name)
        assert response in found_id
        client.list_delete(response)

    def test_get_id_key_specified(self, client):
        list_name = 'jfkldjfkdjfa;kjfkljalkf'
        response = client.list_create(list_name)
        found_id = client.get_id(name=list_name, search_key='lists')
        assert response in found_id
        client.list_delete(response)

    def test_get_by_id_fail(self, client):
        id = 'fklajflkviojaiojhvahjf'
        with pytest.raises(KeyError):
            response = client.get_by_id(id)

    def test_get_by_id_pass(self, client):
        list_name = 'ioavhyuihrvunbcjkva'
        response = client.list_create(list_name)
        returned_dict = client.get_by_id(response)
        assert returned_dict['id'] == response
        client.list_delete(response)

    def test_get_by_id_fail(self, client):
        list_name = 'ioavhyuihrvunbcjkva'
        response = client.list_create(list_name)
        returned_dict = client.get_by_id(response, search_key='tasks')
        assert returned_dict == {}
        client.list_delete(response)

