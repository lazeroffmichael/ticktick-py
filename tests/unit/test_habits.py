from datetime import datetime
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from ticktick.managers.habits import HabitManager


@pytest.fixture(scope='module')
def task_client(fake_client):
    """
    Yields a TasksManager() instance
    Fake client is defined in conftest.py
    """
    yield HabitManager(fake_client)


def default_habit():
    """
    Returns the default habit dictionary
    """
    return [{
        "color": "#97E38B",
        "iconRes": "habit_daily_check_in",
        "createdTime": "2023-01-01T03:00:00+0000",
        "encouragement": "",
        "etag": "40adf35e",
        "goal": 1,
        "id": "641f0e258f0815d68b7b137a",
        "modifiedTime": "2023-01-01T03:00:00+0000",
        "name": "Daily",
        "recordEnable": "false",
        "reminders": [],
        "repeatRule": "RRULE:FREQ=WEEKLY;BYDAY=SU,MO,TU,WE,TH,FR,SA",
        "sortOrder": -6597069766656,
        "status": 0,
        "step": 0,
        "targetDays": 0,
        "targetStartDate": "20230325",
        "totalCheckIns": 0,
        "type": "Boolean",
        "unit": "Count",
        "sectionId": -1,
        "completedCycles": 0,
        "exDates": []
    }]


def example_habit():
    """
    Returns an example habit dictionary
    """

    return [{
        "color": "#FFFFF",
        "iconRes": "habit_meditating",
        "createdTime": "2023-01-01T03:00:00+0000",
        "encouragement": "You can do it!",
        "etag": "40404040",
        "goal": 15,
        "id": "641f0e258f0815d68b7b137a",
        "modifiedTime": "2023-01-01T03:00:00+0000",
        "name": "test-habit",
        "recordEnable": True,
        "reminders": ["TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S"],
        "repeatRule": "RRULE:FREQ=DAILY;INTERVAL=2",
        "sortOrder": -1,
        "status": 1,
        "step": 1,
        "targetDays": 5,
        "targetStartDate": "20230404",
        "totalCheckIns": 2,
        "type": "Real",
        "unit": "Things",
        "sectionId": 2,
        "completedCycles": 1,
        "exDates": ["20230404", "20230406"]
    }]


def example_habit_response():
    """
    Returns an example habit server response dictionary
    """
    return {
        'id2etag': {'641f0e258f0815d68b7b137a': 'hrgz2jxi'},
        'id2error': {}}


class TestInitMethod:

    def test_members_set(self, task_client, fake_client):
        """
        Tests that the appropriate class members are set in the init method
        """
        assert task_client._client == fake_client
        assert task_client.oauth_access_token == fake_client.oauth_manager.access_token_info['access_token']
        assert task_client.oauth_headers == {'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {}'.format(task_client.oauth_access_token),
                                             'User-Agent': fake_client.USER_AGENT}

        fake_client.oauth_manager.access_token_info = None


class TestCreate:

    @freeze_time("2023-01-01 03:00:00")
    def test_create_no_params(self, fake_client):
        with patch('secrets.token_hex', side_effect=['641f0e258f0815d68b7b137a', '40adf35e']), \
                patch('ticktick.api.TickTickClient.http_post', return_value=example_habit_response()):
            response = fake_client.habit.create()
            assert response[0] == example_habit_response()
            assert response[1] == default_habit()

    def test_create_with_params(self, fake_client):
        with patch('secrets.token_hex', side_effect=['641f0e258f0815d68b7b137a']), \
                patch('ticktick.api.TickTickClient.http_post', return_value=example_habit_response()):
            response = fake_client.habit.create(color="#FFFFF", icon="habit_meditating",
                                                created_time=datetime.fromisoformat("2023-01-01T03:00:00"),
                                                encouragement="You can do it!",
                                                etag="40404040", goal=15,
                                                modified_time=datetime.fromisoformat("2023-01-01T03:00:00"),
                                                name="test-habit",
                                                record_enable=True, reminders=["TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S"],
                                                repeat_rule="RRULE:FREQ=DAILY;INTERVAL=2",
                                                sort_order=-1, status=1, step=1, total_checkins=2, habit_type="Real",
                                                unit="Things", section_id=2, target_days=5,
                                                target_start_date="20230404", completed_cycles=1,
                                                ex_dates=["20230404", "20230406"])
            assert response[0] == example_habit_response()
            assert response[1] == example_habit()
