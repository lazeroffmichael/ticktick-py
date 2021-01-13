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


def test_settings(client):
    """Tests _settings() retrieves values"""
    client._settings()
    assert client.profile_id is not None
    assert client.time_zone != ''


def test_get_by_fields_generic(client):
    """Tests getting an id by an object field"""
    list_name = str(uuid.uuid4())
    fake_obj = {'name': list_name}
    client.state['projects'].append(fake_obj)  # Append the fake object
    found = client.get_by_fields(name=list_name)
    assert found
    assert found['name'] == list_name
    client.delete_from_local_state(search='projects', name=list_name)
    assert not client.get_by_fields(name=list_name)


def test_get_by_fields_search_specified(client):
    """Tests getting an id"""
    list_name = str(uuid.uuid4())
    fake_obj = {'name': list_name}
    client.state['projects'].append(fake_obj)  # Append the fake object
    found = client.get_by_fields(name=list_name, search='projects')
    assert found
    assert found['name'] == list_name
    client.delete_from_local_state(search='projects', name=list_name)  # Delete the fake object
    assert not client.get_by_fields(name=list_name)


def test_get_by_fields_no_results(client):
    """Tests getting an empty list if no objects match the fields"""
    name = str(uuid.uuid4())
    assert not client.get_by_fields(name=name)


def test_get_by_fields_search_key_wrong(client):
    """Tests raises an exception when search key doesn't exist"""
    with pytest.raises(KeyError):
        client.get_by_fields(search=str(uuid.uuid4()), name='')


def test_get_by_id_fail(client):
    """Tests returning an empty object if the id doesn't exist"""
    id_str = str(uuid.uuid4())
    assert not client.get_by_id(id_str)


def test_get_by_id_pass(client):
    """Tests getting an object by its id"""
    list_id = str(uuid.uuid4())
    fake_obj = {'id': list_id}
    client.state['projects'].append(fake_obj)  # Append the fake object
    found = client.get_by_id(list_id)
    assert found
    assert found['id'] == list_id
    client.delete_from_local_state(search='projects', id=list_id)  # Delete the fake object
    assert not client.get_by_id(list_id)


def test_get_by_id_search_key_wrong(client):
    """Tests searching in the wrong list wont find the object"""
    list_id = str(uuid.uuid4())
    fake_obj = {'id': list_id}
    client.state['projects'].append(fake_obj)  # Append the fake object
    found = client.get_by_id(list_id, search='tasks')
    assert not found
    client.delete_from_local_state(id=list_id, search='projects')
    assert not client.get_by_id(list_id)


def test_no_args_entered(client):
    with pytest.raises(ValueError):
        client.get_by_fields()
    with pytest.raises(Exception):
        client.get_by_id()
    with pytest.raises(Exception):
        client.get_by_etag()
    with pytest.raises(Exception):
        client.delete_from_local_state()


def test_get_by_etag_pass(client):
    """Tests getting an object by etag works"""
    etag = str(uuid.uuid4())
    obj = {'etag': etag}
    client.state['tags'].append(obj)  # Append the fake object
    assert client.get_by_etag(etag)
    client.delete_from_local_state(etag=etag, search='tags')
    assert not client.get_by_etag(etag)


def test_get_by_etag_fail(client):
    """Asserts that object is empty if the etag doesn't exist"""
    etag = str(uuid.uuid4())
    assert not client.get_by_etag(etag)


def test_delete_from_local_state_pass(client):
    """Tests successfully deleting an item from local state"""
    name = str(uuid.uuid4())
    item = {'name': name}
    client.state['projects'].append(item)  # Append the item to the local state
    obj = client.get_by_fields(name=name, search='projects')  # Make sure append worked
    assert obj
    deleted = client.delete_from_local_state(name=name, search='projects')
    obj = client.get_by_fields(name=name, search='projects')
    assert not obj  # Assert that deletion worked


def test_delete_from_local_state_no_key(client):
    name = str(uuid.uuid4())
    item = {'name': name}
    client.state['projects'].append(item)  # Append the item to the local state
    obj = client.get_by_fields(name=name)  # Make sure append worked
    assert obj
    deleted = client.delete_from_local_state(name=name)
    obj = client.get_by_fields(name=name)  # Search for the object
    assert not obj  # Assert the object doesn't exist anymore


def test_delete_from_local_state_null(client):
    """Tests nothing is deleted if an item doesn't exist"""
    name = str(uuid.uuid4())
    deleted = client.delete_from_local_state(name=name)
    assert not deleted  # Assert that nothing was deleted
