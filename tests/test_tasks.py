"""
Testing module for task functionality
"""
import pytest
import uuid
import datetime
from ticktick.helpers.time_methods import convert_date_to_tick_tick_format




def test_create_subtask_multiple(client):
    parent = client.task.create('Parent Task')
    task1 = client.task.builder('Child Task 1')
    task2 = client.task.builder('Child Task 2')
    task3 = client.task.builder('Child Task 3')
    tasks = [task1, task2, task3]
    tasks = client.task.create(tasks)
    try:
        subtask = client.task.make_subtask(tasks, parent=parent['id'])
    except:
        client.task.delete(parent['id'])  # Delete parent
        client.task.delete([x['id'] for x in tasks])  # Delete children
        assert False
    else:
        ids = [x['id'] for x in subtask]
        ids.append(parent['id'])
        client.task.delete(ids)
        assert subtask[0]['parentId'] == parent['id']
        assert subtask[1]['parentId'] == parent['id']
        assert subtask[2]['parentId'] == parent['id']


def test_create_subtask_type_errors(client):
    objs = ''
    with pytest.raises(TypeError):
        client.task.make_subtask(objs, parent='')
    with pytest.raises(TypeError):
        client.task.make_subtask({}, parent=3)
    with pytest.raises(ValueError):
        client.task.make_subtask({}, parent='Yeah this not right')


def test_create_child_subtask_different_project(client):
    """Tests that an error is raised if the task doesn't exist in the same project as the parent"""
    parent = client.task.create('Parent Task')  # In inbox
    new_proj = client.project.create(str(uuid.uuid4()))  # New project
    task = client.task.builder('Child Task', project=new_proj['id'])  # Create task in the new project
    task = client.task.create([task])  # Create the task
    with pytest.raises(ValueError):
        subtask = client.task.make_subtask(task, parent['id'])  # Make the task a subtask of parent
    client.task.delete([parent['id'], task['id']])
    client.project.delete(new_proj['id'])


def test_move_projects_single_type_errors(client):
    """Tests type erorrs for move_projects"""
    with pytest.raises(TypeError):
        client.task.move('', '')
    with pytest.raises(TypeError):
        client.task.move(123, '')
    with pytest.raises(TypeError):
        client.task.move({}, 342)


def test_move_projects_success(client):
    """Tests moving a single task to a new project"""
    p1 = client.project.builder(str(uuid.uuid4()))
    p2 = client.project.builder(str(uuid.uuid4()))
    p = client.project.create([p1, p2])  # Create the projects
    # Create a tasks in the first project
    task2 = client.task.builder('Task2', project=p[0]['id'])
    task1 = client.task.builder('Task1', project=p[0]['id'])
    tasks = client.task.create([task1, task2])  # Create the tasks
    # Move task1 to p2
    move1 = client.task.move(tasks[0], p[1]['id'])
    # Check that project id for move1 is changed
    assert move1['projectId'] == p[1]['id']
    # Check that task2 still exists in p1
    p1_tasks = client.task.get_from_project(p[0]['id'])
    assert p1_tasks[0] == tasks[1]
    # Check that task1 has moved
    assert client.task.get_from_project(p[1]['id']) == [move1]
    # Delete the objects
    client.project.delete([p[0]['id'], p[1]['id']])  # Tasks are deleted as well.


def test_move_projects_success_multiple(client):
    p0 = client.project.builder(str(uuid.uuid4()))
    p1 = client.project.builder(str(uuid.uuid4()))
    p = client.project.create([p0, p1])  # Create the projects
    task1 = client.task.builder('Task1', project=p[0]['id'])
    task2 = client.task.builder('Task2', project=p[0]['id'])
    task3 = client.task.builder('Task3', project=p[0]['id'])
    tasks = client.task.create([task1, task2, task3])  # Create the tasks in the first project
    # Move task1 and task2 to p1
    move = [tasks[0], tasks[1]]
    moved = client.task.move(move, p[1]['id'])  # Move to p1
    # Make sure task3 still is in p0
    assert client.task.get_from_project(p[0]['id']) == [tasks[2]]
    # Make sure task1 and task2 are in p1
    assert moved[0]['projectId'] == p[1]['id'] and moved[1]['projectId'] == p[1]['id']
    p1_tasks = client.task.get_from_project(p[1]['id'])
    assert moved[0] in p1_tasks and moved[1] in p1_tasks
    client.project.delete([p[0]['id'], p[1]['id']])


def test_move_projects_fail_when_task_projects_differ(client):
    p0 = client.project.builder(str(uuid.uuid4()))
    p1 = client.project.builder(str(uuid.uuid4()))
    p = client.project.create([p0, p1])  # Create the projects
    task1 = client.task.builder('Task1', project=p[0]['id'])
    task2 = client.task.builder('Task2', project=p[1]['id'])
    tasks = client.task.create([task1, task2])
    with pytest.raises(ValueError):
        client.task.move([tasks[0], tasks[1]], client.inbox_id)
    client.project.delete([p[0]['id'], p[1]['id']])
