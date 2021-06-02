"""
Module for testing api.py
"""

import pytest
import httpx
import uuid
import os

from ticktick.api import TickTickClient
from ticktick.managers.projects import ProjectManager
from ticktick.managers.tasks import TaskManager
from ticktick.managers.focus import FocusTimeManager
from ticktick.managers.habits import HabitManager
from ticktick.managers.pomo import PomoManager
from ticktick.managers.settings import SettingsManager
from ticktick.managers.tags import TagsManager
from ticktick.oauth2 import OAuth2
from unittest.mock import patch, Mock


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


class TestDeleteFromLocalState:
    pass
