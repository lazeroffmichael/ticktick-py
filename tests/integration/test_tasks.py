"""
Integration tests for tasks
"""

import pytest
import uuid
import datetime
import time


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

    def test_create_with_date(self, client):
        """
        Tests all day single date
        """
        start = datetime.datetime(2027, 1, 1)
        task = client.task.builder("Task", startDate=start)
        response = client.task.create(task)
        assert response['startDate']
        client.task.delete(response)

    def test_create_with_date_specific(self, client):
        """
        Tests specific single date
        """
        start = datetime.datetime(2027, 1, 1, 14, 30)
        task = client.task.builder("Task", startDate=start)
        response = client.task.create(task)
        assert response['startDate']
        client.task.delete(response)

    def test_create_with_date_range_end_of_month(self, client):
        """
        Tests that having an all day range with start and end of the month works
        """
        start = datetime.datetime(2027, 3, 29)
        end = datetime.datetime(2027, 3, 31)
        task = client.task.builder('test crossing months', startDate=start, dueDate=end)
        response = client.task.create(task)
        assert response['allDay']
        assert response['startDate']
        assert response['dueDate']
        client.task.delete(response)

    def test_create_with_date_range_end_of_year(self, client):
        """
        Tests all day date range when last day is the end of the year
        """
        start = datetime.datetime(2027, 12, 29)
        end = datetime.datetime(2027, 12, 31)
        task = client.task.builder('test crossing year', startDate=start, dueDate=end)
        response = client.task.create(task)
        assert response['allDay']
        assert response['startDate']
        assert response['dueDate']
        client.task.delete(response)

    def test_create_specific_date_range(self, client):
        """
        Tests specific start and end times
        """
        start = datetime.datetime(2027, 12, 5, 14, 30)
        end = datetime.datetime(2027, 12, 7, 16, 30)
        task = client.task.builder('Test Specific Time', startDate=start, dueDate=end)
        response = client.task.create(task)
        assert not response['allDay']
        assert response['startDate']
        assert response['dueDate']
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

#     def test_delete_multiple_tuple(self, client):
#         """
#         Tests multiple created tasks can be deleted if they are passed as a tuple
#         """
#         task1 = example_task()
#         task2 = example_task()
#
#         # create task
#         response1 = client.task.create(task1)
#
#         # create task
#         response2 = client.task.create(task2)
#
#         # delete the tasks
#         deleted = client.task.delete((response1, response2))
#
#         assert deleted == (response1, response2)
#
#
# class TestMoveAll:
#
#     def test_move_list_pass(self, client):
#         """Tests moving all the tasks from one list into a new list"""
#         list1_name = str(uuid.uuid4())
#         list2_name = str(uuid.uuid4())
#         list1 = client.project.create(list1_name)
#         list2 = client.project.create(list2_name)
#         # Tasks will be created in list2
#         task1 = {'title': str(uuid.uuid4()), 'projectId': list2['id']}
#         task2 = {'title': str(uuid.uuid4()), 'projectId': list2['id']}
#         task1 = client.task.create(task1)
#         task2 = client.task.create(task2)
#         # Move the tasks: list2 -> list1
#         move = client.task.move_all(list2['id'], list1['id'])
#         for ids in move:
#             assert ids['id'] == task1['id'] or ids['id'] == task2['id']
#         list2_tasks = client.task.get_from_project(list2['id'])
#         assert not list2_tasks  # Assert that all the tasks in list 2 are gone
#         list1_tasks = client.task.get_from_project(list1['id'])
#         for task in list1_tasks:
#             assert task['projectId'] == list1['id']
#         # Deleting the lists will delete the tasks
#         client.project.delete(list1['id'])
#         client.project.delete(list2['id'])
#
#
# class TestMakeSubtask:
#
#     def test_create_subtask_single(self, client):
#         # Create the parent task
#         parent = client.task.builder('Parent Task')
#         parent = {'title': 'Parent Task'}
#         child = {'title': 'Child Task'}
#         parent_task = client.task.create(parent)
#         child_task = client.task.create(child)
#         try:
#             subtask = client.task.make_subtask(child_task, parent_task['id'])
#         except:
#             client.task.delete(child_task)
#             client.task.delete(parent_task)
#             assert False
#         else:
#             client.task.delete(parent_task)
#             assert client.get_by_id(child_task['id'])  # Make sure child task was not deleted.
#             client.task.delete(child_task)
#             assert subtask['parentId'] == parent_task['id']
#
#     def test_create_subtask_multiple(self, client):
#         """
#         Tests creation of a subtask with multiple tasks
#         """
#         parent = client.task.create({'title': 'Parent Task'})
#         time.sleep(2)
#         task1 = client.task.create({'title': 'Child Task 1'})
#         time.sleep(2)
#         task2 = client.task.create({'title': 'Child Task 2'})
#         time.sleep(2)
#         task3 = client.task.create({'title': 'Child Task 3'})
#         time.sleep(2)
#         try:
#             tasks = [task1, task2, task3]
#             # All should be in the inbox already
#             subtask = client.task.make_subtask(tasks, parent=parent['id'])
#         except:
#             client.task.delete(parent)  # Delete parent
#             # Delete tasks
#             client.task.delete(task1)
#             client.task.delete(task2)
#             client.task.delete(task3)
#             assert False
#         else:
#             retrieved1 = client.get_by_id(obj_id=task1['id'], search='tasks')
#             retrieved2 = client.get_by_id(obj_id=task2['id'], search='tasks')
#             retrieved3 = client.get_by_id(obj_id=task3['id'], search='tasks')
#             client.task.delete(parent)
#             client.task.delete(task1)
#             client.task.delete(task2)
#             client.task.delete(task3)
#             assert retrieved1['parentId'] == parent['id']
#             assert retrieved2['parentId'] == parent['id']
#             assert retrieved3['parentId'] == parent['id']
#
#     def test_create_child_subtask_different_project(self, client):
#         """Tests that an error is raised if the task doesn't exist in the same project as the parent"""
#         parent = client.task.create({'title': 'Parent Task'})  # In inbox
#         new_proj = client.project.create(str(uuid.uuid4()))  # New project
#         time.sleep(2)
#         child = client.task.create({'title': 'Child Task', 'projectId': new_proj['id']})
#         with pytest.raises(ValueError):
#             subtask = client.task.make_subtask(child, parent['id'])  # Make the task a subtask of parent
#         client.task.delete(parent)
#         client.task.delete(child)
#         client.project.delete(new_proj['id'])
#
#
# class TestMoveTasks:
#
#     def test_move_projects_success(self, client):
#         """Tests moving a single task to a new project"""
#         p1 = client.project.builder(str(uuid.uuid4()))
#         p2 = client.project.builder(str(uuid.uuid4()))
#         p = client.project.create([p1, p2])  # Create the projects
#         # Create a tasks in the first project
#         task2 = client.task.create({'title': 'Task2', 'projectId': p[0]['id']})
#         task1 = client.task.create({'title': 'Task1', 'projectId': p[0]['id']})
#         # Move task1 to p2
#         move1 = client.task.move(task1, p[1]['id'])
#         # Check that project id for move1 is changed
#         assert move1['projectId'] == p[1]['id']
#         # Check that task2 still exists in p1
#         p1_tasks = client.task.get_from_project(p[0]['id'])
#         assert p1_tasks
#         # Check that task1 has moved
#         assert client.task.get_from_project(p[1]['id']) == [move1]
#         # Delete the objects
#         client.project.delete([p[0]['id'], p[1]['id']])  # Tasks are deleted as well.
#
#     # def test_move_projects_success_multiple(self, client):
#     #     p0 = client.project.builder(str(uuid.uuid4()))
#     #     p1 = client.project.builder(str(uuid.uuid4()))
#     #     p = client.project.create([p0, p1])  # Create the projects
#     #     task1 = client.task.create({'title': 'Task1', 'projectId': p[0]['id']})
#     #     time.sleep(2)
#     #     task2 = client.task.create({'title': 'Task2', 'projectId': p[0]['id']})
#     #     time.sleep(2)
#     #     task3 = client.task.create({'title': 'Task3', 'projectId': p[0]['id']})
#     #     # Move task1 and task2 to p1
#     #     move = [task1, task2]
#     #     moved = client.task.move(move, p[1]['id'])  # Move to p1
#     #     # Make sure task3 still is in p0
#     #     assert client.task.get_from_project(p[0]['id'])
#     #     # Make sure task1 and task2 are in p1
#     #     assert moved[0]['projectId'] == p[1]['id'] and moved[1]['projectId'] == p[1]['id']
#     #     p1_tasks = client.task.get_from_project(p[1]['id'])
#     #     assert moved[0] in p1_tasks and moved[1] in p1_tasks
#     #     client.project.delete([p[0]['id'], p[1]['id']])
#     #
#     # def test_move_projects_fail_when_task_projects_differ(self, client):
#     #     """
#     #     Tests exception is raised when the project id's differ when trying to move
#     #     """
#     #     p0 = client.project.builder(str(uuid.uuid4()))
#     #     p1 = client.project.builder(str(uuid.uuid4()))
#     #     p = client.project.create([p0, p1])  # Create the projects
#     #     task1 = client.task.create({'title': 'Task1', 'projectId': p[0]['id']})
#     #     time.sleep(2)
#     #     task2 = client.task.create({'title': 'Task2', 'projectId': p[1]['id']})
#     #     with pytest.raises(ValueError):
#     #         client.task.move([task1, task2], client.inbox_id)
#     #     client.project.delete([p[0]['id'], p[1]['id']])
#
#
# class TestMoveAll:
#
#     def test_move_all(self, client):
#         """
#         Tests moving all the tasks in one project to another project
#         """
#         project1 = client.project.builder(str(uuid.uuid4()))
#         project2 = client.project.builder(str(uuid.uuid4()))
#         # Create the projects
#         projects = client.project.create([project1, project2])
#         # Create two tasks
#         task1 = client.task.create({'title': 'Task1', 'projectId': projects[0]['id']})
#         task2 = client.task.create({'title': 'Task2', 'projectId': projects[0]['id']})
#         # Move tasks from first project to second project
#         moved = client.task.move_all(projects[0]['id'], projects[1]['id'])
#         # Make sure that no tasks are in project 1 anymore
#         assert not client.task.get_from_project(projects[0]['id'])
#         # Make sure that there are two tasks in project 2
#         assert len(client.task.get_from_project(projects[1]['id'])) == 2
#         # Delete both projects
#         client.project.delete([projects[0]['id'], projects[1]['id']])
