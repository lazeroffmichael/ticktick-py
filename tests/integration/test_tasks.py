"""
Integration tests for tasks
"""

import pytest
import uuid
import datetime
from ticktick.helpers.time_methods import convert_date_to_tick_tick_format


def example_task():
    return {'title': "Example Task"}


class TestCreate:

    def test_create_only_required_params(self, client):
        """
        Tests a task is created in the inbox
        """
        task = example_task()
        response = client.task.create(task)
        assert response['title'] == task['title']
        assert response['projectId'] == 'inbox'
        assert client.get_by_id(response['id'], search='tasks')
        client.task.delete(response['id'])

    def test_create_empty_dict(self, client):
        """
        Tests empty task dictionary can be created
        """
        response = client.task.create({})
        assert response['title'] == ''
        assert client.get_by_id(response['id'], search='tasks')
        client.task.delete(response['id'])

    def test_create_with_description(self, client):
        """
        Tests a task is created with a description
        """
        task = example_task()
        task['content'] = "This was a created task through ticktick-py"
        response = client.task.create(task)
        assert response['title'] == task['title']
        assert response['content'] == task['content']
        client.task.delete(response['id'])


class TestUpdate:

    def test_update_working(self, client):
        """
        Tests updating a task title
        """
        task = example_task()

        # create the task
        response = client.task.create(task)

        # change the title of the task
        response["title"] = "New Title"

        # update the task
        update = client.task.update(response)

        assert update["title"] == "New Title"  # assert title has changed
        assert update["id"] == response["id"]  # assert id is the same

        client.task.delete(update["id"])

    def test_update_from_local_state(self, client):
        """
        Tests updating still works when the object used is from local state
        """
        task = example_task()

        # create the task
        response = client.task.create(task)

        # get the task from local state
        stored_task = client.get_by_id(response['id'], search='tasks')

        # update task name
        stored_task['title'] = "New Title"

        # update task
        update = client.task.update(stored_task)

        assert update['title'] == stored_task['title']
        assert update['id'] == stored_task['id']
        assert stored_task['id'] == response['id']  # assert that it is still the same task

        client.task.delete(response['id'])


class TestComplete:

    def test_complete(self, client):
        """
        Tests marking a task as complete. Returns an empty string upon successful completion.
        """
        task = example_task()

        # create task
        response = client.task.create(task)

        # mark the task as complete
        completed = client.task.complete(response)

        assert completed == response

    def test_complete_fail(self, client):
        """
        Tests an exception being raised when the task cannot be completed
        """
        task = example_task()

        task['projectId'] = "Nope"
        task['id'] = "Nope"

        # task does not exist to mark as complete
        with pytest.raises(Exception):
            client.task.complete(task)

