"""Testing module for TickTickClient class"""
import pytest
import httpx
import uuid

from ticktick.api import TickTickClient


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


def test_initial_sync(client):
    """Tests sync() retrieves values"""
    client.sync()
    assert client.state['inbox_id'] != ''


def test_settings(client):
    """Tests _settings() retrieves values"""
    client._settings()
    assert client.profile_id is not None
    assert client.time_zone != ''


def test_get_id(client):
    """Tests getting an id by an object field"""
    list_name = str(uuid.uuid4())
    response = client.list.create(list_name)
    found_id = client.get_id(name=list_name)
    assert response in found_id
    client.list.delete(response)


def test_get_id_key_specified(client):
    """Tests getting an id"""
    list_name = str(uuid.uuid4())
    response = client.list.create(list_name)
    found_id = client.get_id(name=list_name, search_key='lists')
    assert response in found_id
    client.list.delete(response)


def test_get_by_id_fail(client):
    id_str = str(uuid.uuid4())
    with pytest.raises(KeyError):
        client.get_by_id(id_str)


def test_get_by_id_pass(client):
    list_name = str(uuid.uuid4())
    response = client.list.create(list_name)
    returned_dict = client.get_by_id(response)
    assert returned_dict['id'] == response
    client.list.delete(response)


def test_get_by_id_fail(client):
    list_name = str(uuid.uuid4())
    response = client.list.create(list_name)
    returned_dict = client.get_by_id(response, search_key='tasks')
    assert returned_dict == {}
    client.list.delete(response)


def test_no_args_entered(client):
    with pytest.raises(ValueError):
        client.get_id()
    with pytest.raises(Exception):
        client.get_by_id()


def test_get_etag(client):
    pass


def test_get_etag_fail_get_by_etag(client):
    etag = str(uuid.uuid4())
    assert client.get_by_etag(etag) == {}


def test_get_etag_fail_get_etag(client):
    with pytest.raises(Exception):
        client.get_by_etag()
        client.get_etag()
