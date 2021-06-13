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
        assert response['projectId'] == client.inbox_id
        assert client.get_by_id(response['id'], search='tasks')
        client.task.delete(response)

    def test_create_empty_dict(self, client):
        """
        Tests empty task dictionary can be created
        """
        response = client.task.create({})
        assert response['title'] == ''
        assert client.get_by_id(response['id'], search='tasks')
        client.task.delete(response)

    def test_create_with_description(self, client):
        """
        Tests a task is created with a description
        """
        task = example_task()
        task['content'] = "This was a created task through ticktick-py"
        response = client.task.create(task)
        assert response['title'] == task['title']
        assert response['content'] == task['content']
        client.task.delete(response)


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

        client.task.delete(response)

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

        client.task.delete(response)


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


class TestDelete:

    def test_delete(self, client):
        """
        Tests a created task can be deleted
        """
        task = example_task()

        # create task
        response = client.task.create(task)

        # delete the task
        deleted = client.task.delete(response)

        assert deleted == response

    def test_delete_multiple(self, client):
        """
        Tests multiple created tasks can be deleted
        """
        task1 = example_task()
        task2 = example_task()

        # create task
        response1 = client.task.create(task1)

        # create task
        response2 = client.task.create(task2)

        # delete the tasks
        deleted = client.task.delete([response1, response2])

        assert deleted == [response1, response2]

    def test_delete_multiple_tuple(self, client):
        """
        Tests multiple created tasks can be deleted if they are passed as a tuple
        """
        task1 = example_task()
        task2 = example_task()

        # create task
        response1 = client.task.create(task1)

        # create task
        response2 = client.task.create(task2)

        # delete the tasks
        deleted = client.task.delete((response1, response2))

        assert deleted == (response1, response2)


class TestMoveAll:

    def test_move_list_pass(self, client):
        """Tests moving all the tasks from one list into a new list"""
        list1_name = str(uuid.uuid4())
        list2_name = str(uuid.uuid4())
        list1 = client.project.create(list1_name)
        list2 = client.project.create(list2_name)
        # Tasks will be created in list2
        task1 = {'title': str(uuid.uuid4()), 'projectId': list2['id']}
        task2 = {'title': str(uuid.uuid4()), 'projectId': list2['id']}
        task1 = client.task.create(task1)
        task2 = client.task.create(task2)
        # Move the tasks: list2 -> list1
        move = client.task.move_all(list2['id'], list1['id'])
        for ids in move:
            assert ids['id'] == task1['id'] or ids['id'] == task2['id']
        list2_tasks = client.task.get_from_project(list2['id'])
        assert not list2_tasks  # Assert that all the tasks in list 2 are gone
        list1_tasks = client.task.get_from_project(list1['id'])
        for task in list1_tasks:
            assert task['projectId'] == list1['id']
        # Deleting the lists will delete the tasks
        client.project.delete(list1['id'])
        client.project.delete(list2['id'])


class TestMakeSubtask:

    def test_create_subtask_single(self, client):
        # Create the parent task
        parent = client.task.builder('Parent Task')
        parent = {'title': 'Parent Task'}
        child = {'title': 'Child Task'}
        parent_task = client.task.create(parent)
        child_task = client.task.create(child)
        try:
            subtask = client.task.make_subtask(child_task, parent_task['id'])
        except:
            client.task.delete(child_task)
            client.task.delete(parent_task)
            assert False
        else:
            client.task.delete(parent_task)
            assert client.get_by_id(child_task['id'])  # Make sure child task was not deleted.
            client.task.delete(child_task)
            assert subtask['parentId'] == parent_task['id']
