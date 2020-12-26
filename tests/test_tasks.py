"""
Testing module for task functionality
"""
import pytest
import uuid


def test_create_task_just_title(client):
    """Tests task creation with just title"""
    title = 'iovhaoh48hh94u90q09h4hgihfkanvl'
    task = client.task.create(title)
    task_obj = client.get_by_id(task)
    assert task_obj
    assert task_obj['projectId'] == client.state['inbox_id']


def test_delete_task(client):
    """Tests task deletion"""
    name = 'iovhaoh48hh94u90q09h4hgihfkanvl'
    # Find the task
    task_find = client.get_id(title=name)
    delete = client.task.delete(task_find[0])
    # Make sure the id doesn't exist
    make_sure = client.get_by_id(delete)
    assert not make_sure


def test_create_task_title_and_priority(client):
    """Tests task creation for title and priority"""
    title = str(uuid.uuid4())
    priority = 3  # Medium
    task = client.task.create(title, priority=priority)
    task_obj = client.get_by_id(task)
    assert task_obj  # Make sure object was created
    assert task_obj['priority'] == priority  # Assert priority matches
    client.task.delete(task)  # Delete task


def test_create_task_title_and_priority_fail(client):
    """Tests task creation for invalid priority value"""
    title = str(uuid.uuid4())
    priority = 56
    with pytest.raises(ValueError):
        client.task.create(title, priority=priority)


def test_create_task_different_list(client):
    """Tests task creation with set project id"""
    list_title = str(uuid.uuid4())
    list_id = client.list.create(list_title)  # Create list
    task_title = str(uuid.uuid4())
    task_id = client.task.create(task_title, list_id=list_id, priority=3)  # Create task in list
    get_task = client.get_by_id(task_id)
    assert get_task
    assert get_task['projectId'] == list_id
    client.list.delete(list_id)
    client.task.delete(task_id)


def test_create_task_different_list_fail(client):
    """Tests exception thrown if list doesn't exist"""
    with pytest.raises(ValueError):
        client.task.create(str(uuid.uuid4()), list_id=str(uuid.uuid4()))


def test_create_task_with_tags(client):
    """Tests creating a list with tags"""
    # tag = [str(uuid.uuid4())]
    # title = str(uuid.uuid4())
    # task_id = client.task_create(title, tags=tag)
    # task_obj = client.get_by_id(task_id)
    # assert task_obj
    # assert task_obj['tags'] == tag
    # # Delete the tags
