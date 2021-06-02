"""
Module for testing api.py
"""

import pytest
import uuid

from ticktick.api import TickTickClient
from ticktick.managers.projects import ProjectManager
from ticktick.managers.tasks import TaskManager
from ticktick.managers.focus import FocusTimeManager
from ticktick.managers.habits import HabitManager
from ticktick.managers.pomo import PomoManager
from ticktick.managers.settings import SettingsManager
from ticktick.managers.tags import TagsManager
from ticktick.oauth2 import OAuth2
from unittest.mock import patch


@pytest.yield_fixture(scope='module')
def ticktick_client():
    user = str(uuid.uuid4())
    passw = str(uuid.uuid4())
    client_id = str(uuid.uuid4())
    client_secret = str(uuid.uuid4())
    redirect = str(uuid.uuid4())
    with patch('ticktick.oauth2.OAuth2.get_access_token'):
        oauth = OAuth2(client_id=client_id, client_secret=client_secret, redirect_uri=redirect)

    with patch('ticktick.api.TickTickClient._prepare_session'):
        client = TickTickClient(user, passw, oauth)

    yield client


def mocked_request(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

    if args[0] == 'http://someurl.com/test.json':
        return MockResponse({"key1": "value1"}, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({"key2": "value2"}, 200)

    return MockResponse(None, 404)


class TestInitMethod:

    def test_init_class_members_set(self, ticktick_client):
        """
        Tests all class members are set in the init method
        """
        client = ticktick_client

        assert client.access_token == ''
        assert client.cookies == {}
        assert client.time_zone == ''
        assert client.profile_id == ''
        assert client.inbox_id == ''
        assert len(client.state) == 6
        assert isinstance(client.oauth_manager, OAuth2)
        assert client._session == client.oauth_manager.session
        assert isinstance(client.focus, FocusTimeManager)
        assert isinstance(client.habit, HabitManager)
        assert isinstance(client.project, ProjectManager)
        assert isinstance(client.pomo, PomoManager)
        assert isinstance(client.settings, SettingsManager)
        assert isinstance(client.tag, TagsManager)
        assert isinstance(client.task, TaskManager)


class TestPrepareSession:

    @patch('ticktick.api.TickTickClient._login')
    @patch('ticktick.api.TickTickClient._settings')
    @patch('ticktick.api.TickTickClient.sync')
    def test_prepare_session_success(self,
                                     mock1,
                                     mock2,
                                     mock3,
                                     ticktick_client):
        """
        Tests prepare session makes necessary calls
        """
        # logging in return value
        mock1.return_value = None
        # settings return value
        mock2.return_value = None
        # sync return value
        mock3.return_value = None

        ticktick_client._prepare_session('username', 'password')


class TestResetLocalState:

    def test_reset_local_state(self, ticktick_client):
        """
        Tests resetting of the local state dictionary
        """
        ticktick_client.reset_local_state()
        assert len(ticktick_client.state) == 6
        for item in ticktick_client.state:
            assert not ticktick_client.state[item]


class TestLoggingIn:

    def test_logging_in(self, ticktick_client):
        """
        Tests logging in sets the access token and 't' in the cookies
        dictionary upon response from the post request
        """
        returned_dictionary = {'token': str(uuid.uuid4())}
        with patch('ticktick.api.TickTickClient.http_post',
                   return_value=returned_dictionary):
            ticktick_client._login('username', 'password')

        assert ticktick_client.access_token == returned_dictionary['token']
        assert ticktick_client.cookies['t'] == ticktick_client.access_token

        ticktick_client.access_token = ''
        ticktick_client.cookies = {}


class TestCheckingStatusCode:

    def test_check_status_code(self, ticktick_client):
        """
        Tests that a runtime error is raised when the response.status_code != 200
        """
        mocked_httpx_response = mocked_request(['404'])
        with pytest.raises(RuntimeError):
            ticktick_client.check_status_code(mocked_httpx_response, 'Failed')


class TestFetchSettings:

    def test_settings(self, ticktick_client):
        """
        Tests that time_zone and profile_id are set
        """
        returned_dictionary = {'timeZone': 'US/Pacific',
                               'id': str(uuid.uuid4())}
        with patch('ticktick.api.TickTickClient.http_get',
                   return_value=returned_dictionary):
            returned = ticktick_client._settings()

        assert ticktick_client.time_zone == returned_dictionary['timeZone']
        assert ticktick_client.profile_id == returned_dictionary['id']
        assert returned == returned_dictionary

        ticktick_client.time_zone = ''
        ticktick_client.profile_id = ''


class TestSync:

    def test_sync(self, ticktick_client):
        """
        Tests sync sets the proper class members
        """
        d = {
            'inboxId': str(uuid.uuid4()),
            'projectGroups': str(uuid.uuid4()),
            'projectProfiles': str(uuid.uuid4()),
            'syncTaskBean': {'update': str(uuid.uuid4())},
            'tags': [str(uuid.uuid4())]
        }
        with patch('ticktick.api.TickTickClient.http_get',
                   return_value=d):
            response = ticktick_client.sync()

        assert response == d
        assert ticktick_client.inbox_id == d['inboxId']
        assert ticktick_client.state['project_folders'] == d['projectGroups']
        assert ticktick_client.state['projects'] == d['projectProfiles']
        assert ticktick_client.state['tasks'] == d['syncTaskBean']['update']
        assert ticktick_client.state['tags'] == d['tags']

        ticktick_client.inbox_id = ''
        ticktick_client.reset_local_state()


class TestParseMethods:

    def test_parse_id(self, ticktick_client):
        """
        Tests proper parsing of the ID from a dictionary
        """
        d = {'id2etag': {'5ff2bcf68f08093e5b745a30': '3okkc2xm'}, 'id2error': {}}
        expected_id = '5ff2bcf68f08093e5b745a30'
        assert ticktick_client.parse_id(d) == expected_id

    def test_parse_etag(self, ticktick_client):
        """
        Tests proper parsing of the ID from an Etag response
        """
        d = {"id2etag": {"MyTag": "vxzpwo38"}, "id2error": {}}
        expected_etag = "vxzpwo38"
        assert ticktick_client.parse_etag(d) == expected_etag

    def test_parse_multiple_etags(self, ticktick_client):
        """
        Tests proper parsing of multiple ID's from an Etag response
        """
        d = {'id2etag': {"MyTag": "vxzpwo38", "MyTag2": "vxzpwo38"},
             "id2error": {}}
        expected_etags = ["vxzpwo38", "vxzpwo38"]
        returned = ticktick_client.parse_etag(d, multiple=True)
        assert len(returned) == 2
        assert expected_etags[0] in returned
        assert expected_etags[1] in returned


class TestGetByFields:

    def test_get_by_fields_generic(self, ticktick_client):
        """
        Tests getting an id by an object field
        """
        list_name = str(uuid.uuid4())
        fake_obj = {'name': list_name}
        ticktick_client.state['projects'].append(fake_obj)  # Append the fake object
        found = ticktick_client.get_by_fields(name=list_name)
        assert found
        assert found['name'] == list_name
        ticktick_client.delete_from_local_state(search='projects', name=list_name)
        assert not ticktick_client.get_by_fields(name=list_name)

    def test_get_by_fields_search_specified(self, ticktick_client):
        """
        Tests getting an id
        """
        list_name = str(uuid.uuid4())
        fake_obj = {'name': list_name}
        ticktick_client.state['projects'].append(fake_obj)  # Append the fake object
        found = ticktick_client.get_by_fields(name=list_name, search='projects')
        assert found
        assert found['name'] == list_name
        ticktick_client.delete_from_local_state(search='projects', name=list_name)  # Delete the fake object
        assert not ticktick_client.get_by_fields(name=list_name)

    def test_get_by_fields_no_results(self, ticktick_client):
        """
        Tests getting an empty list if no objects match the fields
        """
        name = str(uuid.uuid4())
        assert not ticktick_client.get_by_fields(name=name)

    def test_get_by_fields_search_key_wrong(self, ticktick_client):
        """
        Tests raises an exception when search key doesn't exist
        """
        with pytest.raises(KeyError):
            ticktick_client.get_by_fields(search=str(uuid.uuid4()), name='')


class TestGetByID:

    def test_get_by_id_fail(self, ticktick_client):
        """
        Tests returning an empty object if the id doesn't exist
        """
        id_str = str(uuid.uuid4())
        assert not ticktick_client.get_by_id(id_str)

    def test_get_by_id_pass(self, ticktick_client):
        """
        Tests getting an object by its id
        """
        list_id = str(uuid.uuid4())
        fake_obj = {'id': list_id}
        ticktick_client.state['projects'].append(fake_obj)  # Append the fake object
        found = ticktick_client.get_by_id(list_id)
        assert found
        assert found['id'] == list_id
        ticktick_client.delete_from_local_state(search='projects', id=list_id)  # Delete the fake object
        assert not ticktick_client.get_by_id(list_id)

    def test_get_by_id_search_key_wrong(self, ticktick_client):
        """
        Tests searching in the wrong list wont find the object
        """
        list_id = str(uuid.uuid4())
        fake_obj = {'id': list_id}
        ticktick_client.state['projects'].append(fake_obj)  # Append the fake object
        found = ticktick_client.get_by_id(list_id, search='tasks')
        assert not found
        ticktick_client.delete_from_local_state(id=list_id, search='projects')
        assert not ticktick_client.get_by_id(list_id)

    def test_no_args_entered(self, ticktick_client):
        """
        Tests exceptions raised when no arguments passed
        """
        with pytest.raises(ValueError):
            ticktick_client.get_by_fields()
        with pytest.raises(Exception):
            ticktick_client.get_by_id()
        with pytest.raises(Exception):
            ticktick_client.get_by_etag()
        with pytest.raises(Exception):
            ticktick_client.delete_from_local_state()


class TestGetByEtag:

    def test_get_by_etag_pass(self, ticktick_client):
        """
        Tests getting an object by etag works
        """
        etag = str(uuid.uuid4())
        obj = {'etag': etag}
        ticktick_client.state['tags'].append(obj)  # Append the fake object
        assert ticktick_client.get_by_etag(etag)
        ticktick_client.delete_from_local_state(etag=etag, search='tags')
        assert not ticktick_client.get_by_etag(etag)

    def test_get_by_etag_fail(self, ticktick_client):
        """
        Asserts that object is empty if the etag doesn't exist
        """
        etag = str(uuid.uuid4())
        assert not ticktick_client.get_by_etag(etag)


class TestDeleteFromLocalState:

    def test_delete_from_local_state_pass(self, ticktick_client):
        """
        Tests successfully deleting an item from local state
        """
        name = str(uuid.uuid4())
        item = {'name': name}
        ticktick_client.state['projects'].append(item)  # Append the item to the local state
        obj = ticktick_client.get_by_fields(name=name, search='projects')  # Make sure append worked
        assert obj
        deleted = ticktick_client.delete_from_local_state(name=name, search='projects')
        obj = ticktick_client.get_by_fields(name=name, search='projects')
        assert not obj  # Assert that deletion worked

    def test_delete_from_local_state_no_key(self, ticktick_client):
        """
        Tests finding the object without a key entered
        """
        name = str(uuid.uuid4())
        item = {'name': name}
        ticktick_client.state['projects'].append(item)  # Append the item to the local state
        obj = ticktick_client.get_by_fields(name=name)  # Make sure append worked
        assert obj
        deleted = ticktick_client.delete_from_local_state(name=name)
        obj = ticktick_client.get_by_fields(name=name)  # Search for the object
        assert not obj  # Assert the object doesn't exist anymore

    def test_delete_from_local_state_null(self, ticktick_client):
        """
        Tests nothing is deleted if an item doesn't exist
        """
        name = str(uuid.uuid4())
        deleted = ticktick_client.delete_from_local_state(name=name)
        assert not deleted  # Assert that nothing was deleted
