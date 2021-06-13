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

    @patch('ticktick.api.TickTickClient.sync')
    def test_create_make_inbox_id(self, mock_object, task_client, fake_client):
        """
        Tests that when the project id is 'inbox' that it is set to the users actual inbox id
        """
        mock_object.return_value = None
        return_value = example_task_response()
        return_value['projectId'] = 'inbox'
        with patch('ticktick.api.TickTickClient.http_post', return_value=return_value):
            task = task_client.create(return_value)
            assert task['projectId'] == fake_client.inbox_id

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


class TestBuilder:

    def test_builder_method(self, task_client):
        """
        Tests builder method works with just the title
        """
        task = task_client.builder("Example")
        assert task['title'] == "Example"
        assert len(task) == 1

    def test_builder_method_all(self, task_client):
        """
        Tests setting all builder methods
        """
        start = datetime.datetime(2, 5, 12)
        end = datetime.datetime(2, 7, 12)
        task = task_client.builder(title="Title",
                                   content="Content",
                                   desc="Desc",
                                   allDay=False,
                                   startDate=start,
                                   dueDate=end,
                                   timeZone="US/Pacific",
                                   reminders=['none'],
                                   repeat='Nope',
                                   priority=3,
                                   sortOrder=4645345,
                                   items=[])
        assert len(task) == 12
        assert task['title'] == "Title"
        assert task['content'] == "Content"
        assert task['desc'] == "Desc"
        assert not task["allDay"]
        assert task["startDate"] == start
        assert task["dueDate"] == end
        assert task["timeZone"] == "US/Pacific"
        assert task["reminders"] == ['none']
        assert task["repeat"] == "Nope"
        assert task["priority"] == 3
        assert task["sortOrder"] == 4645345
        assert task["items"] == []


class TestGetFromProject:

    def test_get_from_list(self, fake_client):
        """Tests getting all the tasks from a list"""
        # Make a fake list
        fake_list_id = str(uuid.uuid4())
        fake_list = {'id': fake_list_id}
        fake_client.state['projects'].append(fake_list)  # Append the fake list
        # Make some fake tasks
        task1_title = str(uuid.uuid4())
        task2_title = str(uuid.uuid4())
        task1 = {'projectId': fake_list_id, 'title': task1_title}
        task2 = {'projectId': fake_list_id, 'title': task2_title}
        # Append fake tasks
        fake_client.state['tasks'].append(task1)
        fake_client.state['tasks'].append(task2)
        tasks = fake_client.task.get_from_project(fake_list_id)
        assert task1 in tasks and task2 in tasks
        # Delete the fake objects
        fake_client.delete_from_local_state(id=fake_list_id, search='projects')
        fake_client.delete_from_local_state(title=task1_title, search='tasks')
        fake_client.delete_from_local_state(title=task2_title, search='tasks')

    def test_get_from_list_single(self, fake_client):
        # Make a fake list
        fake_list_id = str(uuid.uuid4())
        fake_list = {'id': fake_list_id}
        fake_client.state['projects'].append(fake_list)  # Append the fake list
        # Make some fake tasks
        task1_title = str(uuid.uuid4())
        task1 = {'projectId': fake_list_id, 'title': task1_title}
        fake_client.state['tasks'].append(task1)
        tasks = fake_client.task.get_from_project(fake_list_id)
        assert tasks[0] == task1
        fake_client.delete_from_local_state(id=fake_list_id, search='projects')
        fake_client.delete_from_local_state(title=task1_title, search='tasks')

    def test_get_from_list_error(self, fake_client):
        """Tests exception raised if list doesn't exist"""
        with pytest.raises(ValueError):
            fake_client.task.get_from_project(str(uuid.uuid4()))


class TestTimeConversions:

    def test_time_checks_start_after_end(self, task_client):
        """Tests exception raised if start date after end date"""
        start = datetime.datetime(2022, 1, 5)
        end = datetime.datetime(2022, 1, 2)
        with pytest.raises(ValueError):
            task_client.time_conversions(start_date=start, end_date=end)

    def test_invalid_time_zone(self, task_client):
        """Tests exception raised if time zone not valid"""
        tz = 'Yeah this not right'
        with pytest.raises(ValueError):
            task_client.time_conversions(time_zone=tz)

    def test_time_checks_proper_parse_start(self, fake_client):
        """Tests proper parsing of date with only start_date"""
        fake_client.time_zone = "US/Pacific"
        start = datetime.datetime(2022, 1, 5)
        dates = fake_client.task.time_conversions(start)
        assert dates['startDate'] == convert_date_to_tick_tick_format(start, tz=fake_client.time_zone)
        assert dates['dueDate'] == convert_date_to_tick_tick_format(start, tz=fake_client.time_zone)
        assert dates['isAllDay']
        fake_client.time_zone = ''

    def test_time_checks_proper_parse_end(self, fake_client):
        fake_client.time_zone = "US/Pacific"
        end = datetime.datetime(2022, 1, 5)
        dates = fake_client.task.time_conversions(end)
        assert dates['startDate'] == convert_date_to_tick_tick_format(end, tz=fake_client.time_zone)
        assert dates['dueDate'] == convert_date_to_tick_tick_format(end, tz=fake_client.time_zone)
        assert dates['isAllDay']
        fake_client.time_zone = ''

    def test_time_checks_proper_parse_start_not_all_day(self, fake_client):
        """Tests proper date parse of not all day"""
        fake_client.time_zone = "US/Pacific"
        start = datetime.datetime(2022, 1, 5, 14, 56, 34)
        dates = fake_client.task.time_conversions(start)
        assert dates['startDate'] == convert_date_to_tick_tick_format(start, tz=fake_client.time_zone)
        assert dates['dueDate'] == convert_date_to_tick_tick_format(start, tz=fake_client.time_zone)
        assert not dates['isAllDay']
        fake_client.time_zone = ''

    def test_time_checks_proper_parse_end_not_all_day(self, fake_client):
        fake_client.time_zone = "US/Pacific"
        end = datetime.datetime(2022, 1, 5, 16, 56, 45)
        dates = fake_client.task.time_conversions(end)
        assert dates['startDate'] == convert_date_to_tick_tick_format(end, tz=fake_client.time_zone)
        assert dates['dueDate'] == convert_date_to_tick_tick_format(end, tz=fake_client.time_zone)
        assert not dates['isAllDay']
        fake_client.time_zone = ''

    def test_time_all_day_range(self, fake_client):
        fake_client.time_zone = "US/Pacific"
        start = datetime.datetime(2022, 1, 5)
        end = datetime.datetime(2022, 1, 8)
        expected = datetime.datetime(2022, 1, 9)
        dates = fake_client.task.time_conversions(start, end)
        assert dates['startDate'] == convert_date_to_tick_tick_format(start, tz=fake_client.time_zone)
        assert dates['dueDate'] == convert_date_to_tick_tick_format(expected, tz=fake_client.time_zone)
        assert dates['isAllDay']
        fake_client.time_zone = ''

    def test_time_all_day_range_end_of_month(self, fake_client):
        fake_client.time_zone = "US/Pacific"
        start = datetime.datetime(2022, 1, 28)
        end = datetime.datetime(2022, 1, 31)
        expected = datetime.datetime(2022, 2, 1)
        dates = fake_client.task.time_conversions(start, end)
        assert dates['startDate'] == convert_date_to_tick_tick_format(start, tz=fake_client.time_zone)
        assert dates['dueDate'] == convert_date_to_tick_tick_format(expected, tz=fake_client.time_zone)
        assert dates['isAllDay']
        fake_client.time_zone = ''

    def test_time_all_day_range_end_of_year(self, fake_client):
        fake_client.time_zone = "US/Pacific"
        start = datetime.datetime(2022, 12, 28)
        end = datetime.datetime(2022, 12, 31)
        expected = datetime.datetime(2023, 1, 1)
        dates = fake_client.task.time_conversions(start, end)
        assert dates['startDate'] == convert_date_to_tick_tick_format(start, tz=fake_client.time_zone)
        assert dates['dueDate'] == convert_date_to_tick_tick_format(expected, tz=fake_client.time_zone)
        assert dates['isAllDay']
        fake_client.time_zone = ''

    def test_not_datetime(self, fake_client):
        """
        Tests TypeError is raised when start or end are not a datetime object
        """
        fake_client.time_zone = "US/Pacific"
        start = 'Nope'
        end = 'Nope'
        with pytest.raises(TypeError):
            fake_client.task.time_conversions(start, end)
        fake_client.time_zone = ''

    def test_not_datetime_end(self, fake_client):
        """
        Tests TypeError is raised whene start or end are not a datetime object
        """
        fake_client.time_zone = "US/Pacific"
        start = datetime.datetime(2022, 1, 28)
        end = 'Nope'
        with pytest.raises(TypeError):
            fake_client.task.time_conversions(start, end)
        fake_client.time_zone = ''

    def test_start_not_all_day(self, fake_client):
        """
        Tests that all day is false if start time is given
        """
        fake_client.time_zone = "US/Pacific"
        start = datetime.datetime(2022, 1, 28, 14, 30)
        dates = fake_client.task.time_conversions(start)
        assert not dates['isAllDay']
        fake_client.time_zone = ''
