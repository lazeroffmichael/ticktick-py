"""
Unit test module for tasks.py
"""

import pytest
import uuid
import datetime

from ticktick.helpers.time_methods import convert_date_to_tick_tick_format
from ticktick.managers.tasks import TaskManager
from unittest.mock import patch


@pytest.yield_fixture(scope='module')
def task_client(fake_client):
    """
    Yields a TasksManager() instance
    Fake client is defined in conftest.py
    """
    yield TaskManager(fake_client)


def example_task_response():
    """
    Returns an example task dictionary
    """
    return {
        "id": "String",
        "projectId": "String",
        "title": "Task Title",
        "content": "Task Content",
        "desc": "Task Description",
        "allDay": True,
        "startDate": "2019-11-13T03:00:00+0000",
        "dueDate": "2019-11-14T03:00:00+0000",
        "timeZone": "America/Los_Angeles",
        "reminders": ["TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S"],
        "repeat": "RRULE:FREQ=DAILY;INTERVAL=1",
        "priority": 1,
        "status": 0,
        "completedTime": "2019-11-13T03:00:00+0000",
        "sortOrder": 12345,
        "items": [{
            "id": "String",
            "status": 1,
            "title": "Subtask Title",
            "sortOrder": 12345,
            "startDate": "2019-11-13T03:00:00+0000",
            "isAllDay": False,
            "timeZone": "America/Los_Angeles",
            "completedTime": "2019-11-13T03:00:00+0000"
        }]
    }


class TestInitMethod:

    def test_members_set(self, task_client, fake_client):
        """
        Tests that the appropriate class members are set in the init method
        """
        assert task_client._client == fake_client
        assert task_client.oauth_access_token == fake_client.oauth_manager.access_token_info['access_token']
        assert task_client.headers == {'Content-Type': 'application/json',
                                       'Authorization': 'Bearer {}'.format(task_client.oauth_access_token)}

        fake_client.oauth_manager.access_token_info = None


class TestCreate:

    def test_generate_create_url(self, task_client):
        """
        Tests url endpoint for task creation is returned properly
        """
        expected_create_url = 'https://api.ticktick.com/open/v1/task'
        actual_url = task_client._generate_create_url()
        assert expected_create_url == actual_url

    @patch('ticktick.api.TickTickClient.sync')
    def test_create(self, mock_object, task_client):
        """
        Tests that response dictionary is returned from create method
        """
        mock_object.return_value = None
        with patch('ticktick.api.TickTickClient.http_post', return_value=example_task_response()):
            assert task_client.create({}) == example_task_response()


class TestUpdate:

    def test_generate_update_url(self, task_client):
        """
        Tests url endpoint for updating a task is returned properly
        """
        task = example_task_response()
        expected_update_url = f"https://api.ticktick.com/open/v1/task/{task['id']}"
        actual_url = task_client._generate_update_url(task['id'])
        assert expected_update_url == actual_url

    @patch('ticktick.api.TickTickClient.sync')
    def test_update(self, mock_object, task_client):
        """
        Tests that response dictionary is returned from update method
        """
        mock_object.return_value = None

        updated_response = example_task_response()
        updated_response['title'] = "New Title"

        with patch('ticktick.api.TickTickClient.http_post', return_value=updated_response):
            assert task_client.update(updated_response) == updated_response

    def test_update_fail_empty_task(self, task_client):
        """
        Tests an exception is raised when the task dictionary passed is not valid
        """
        task = {}

        # update the task -> raises a KeyError since task['id'] doesn't exist
        with pytest.raises(Exception):
            task_client.update(task)


class TestComplete:

    def test_generate_mark_complete_url(self, task_client):
        """
        Tests url endpoint for marking a task as complete is returned properly
        """
        task = example_task_response()

        expected_complete_url = f"https://api.ticktick.com/open/v1/project/{task['projectId']}/task/{task['id']}"
        expected_complete_url += "/complete"

        actual_url = task_client._generate_mark_complete_url(task['projectId'], task['id'])

        assert expected_complete_url == actual_url

    @patch('ticktick.api.TickTickClient.sync')
    def test_complete(self, mock_object, task_client):
        """
        Tests complete() returns a dictionary
        """
        mock_object.return_value = None

        task = example_task_response()

        # have status as one to mark as complete
        task['status'] = 1

        with patch('ticktick.api.TickTickClient.http_post', return_value=task):
            assert task_client.complete(task) == task

    @patch('ticktick.api.TickTickClient.sync')
    def test_complete_returns_empty(self, mock_object, task_client):
        """
        Tests complete() returns a '' (this is the normal recurrence from the post request)
        """
        mock_object.return_value = None

        task = example_task_response()

        # have status as one to mark as complete
        task['status'] = 1

        with patch('ticktick.api.TickTickClient.http_post', return_value=''):
            assert task_client.complete(task) == task


class TestDelete:

    def test_generate_delete_url(self, task_client):
        """
        Tests delete url is generated correctly
        """
        expected = "https://api.ticktick.com/api/v2/batch/task"
        assert expected == task_client._generate_delete_url()

    @patch('ticktick.api.TickTickClient.sync')
    def test_delete_single_dict(self, mock_object, task_client):
        """
        Tests deleting a single dictionary
        """
        mock_object.return_value = None

        task = example_task_response()

        with patch('ticktick.api.TickTickClient.http_post', return_value={}):
            assert task_client.delete(task) == task

    @patch('ticktick.api.TickTickClient.sync')
    def test_delete_single_dict_project_inbox(self, mock_object, task_client):
        """
        Tests setting the 'projectId' when it is inbox
        """
        mock_object.return_value = None

        task = example_task_response()
        task['projectId'] = "inbox"

        with patch('ticktick.api.TickTickClient.http_post', return_value={}):
            assert task_client.delete(task) == task

    @patch('ticktick.api.TickTickClient.sync')
    def test_delete_multiple_dicts(self, mock_object, task_client):
        """
        Tests deleting multiple dictionaries
        """
        mock_object.return_value = None

        task1 = example_task_response()
        task2 = example_task_response()
        task3 = example_task_response()

        tasks = [task1, task2, task3]

        with patch('ticktick.api.TickTickClient.http_post', return_value={}):
            assert task_client.delete(tasks) == tasks

    @patch('ticktick.api.TickTickClient.sync')
    def test_delete_multiple_dicts_project_id_inbox(self, mock_object, task_client):
        """
        Tests deleting multiple dictionaries when the project_id of a task is "inbox"
        """
        mock_object.return_value = None

        task1 = example_task_response()
        task2 = example_task_response()
        task2['projectId'] = "inbox"
        task3 = example_task_response()

        tasks = [task1, task2, task3]

        with patch('ticktick.api.TickTickClient.http_post', return_value={}):
            assert task_client.delete(tasks) == tasks
