"""
Testing module for ListManager class
"""
import pytest
import uuid


def test_create_list_success(client):
    """Tests creating a list and having it populate the class list dictionary"""
    name = str(uuid.uuid4())
    color = "#e070ff"
    task = client.list.create(name, color)
    assert task['name'] == name
    client.list.delete(task['id'])


def test_update_success(client):
    """Tests updating an already existing list"""
    name = str(uuid.uuid4())
    task = client.list.create(name)
    assert task['name'] == name
    update_name = str(uuid.uuid4())
    task['name'] = update_name
    task2 = client.list.update(task['id'])
    assert task2['name'] == update_name
    client.list.delete(task2['id'])


def test_create_list_type_note_success(client):
    """Tests creating a list with type note"""
    name = str(uuid.uuid4())
    color = "#b20000"
    list_type = 'NOTE'
    task = client.list.create(name, color, list_type)
    assert task['kind'] == list_type
    client.list.delete(task['id'])


def test_create_list_duplicate_failure(client):
    """Tests no list creation if the same name already exists"""
    name = str(uuid.uuid4())
    duplicate_name = name
    task = client.list.create(name)
    with pytest.raises(ValueError):
        client.list.create(duplicate_name)
    client.list.delete(task['id'])


def test_delete_list_pass(client):
    """Tests list is properly deleted"""
    # Get id for 'Created List From Python'
    name = str(uuid.uuid4())
    name2 = str(uuid.uuid4())
    task1 = client.list.create(name)
    task2 = client.list.create(name2)
    # Delete List
    task1 = client.list.delete(task1['id'])
    task2 = client.list.delete(task2['id'])
    obj1 = client.get_by_id(task1['id'])
    obj2 = client.get_by_id(task2['id'])
    assert not obj1
    assert not obj2


def test_delete_list_fail(client):
    """Tests deletion will not occur if list name does not exist"""
    list_id = str(uuid.uuid4())
    with pytest.raises(KeyError):
        client.list.delete(list_id)


def test_delete_list_preserve_tasks_inbox(client):
    """Tests deleting a list but having preserve tasks enabled"""
    list_name = str(uuid.uuid4())
    list_obj = client.list.create(list_name)
    # Create a task inside the list
    task_name = str(uuid.uuid4())
    task_obj = client.task.create(task_name, list_id=list_obj['id'])
    assert task_obj['projectId'] == list_obj['id']
    # Delete the list with the preserve_task flag enabled
    delete = client.list.delete(list_obj['id'], preserve_tasks=True)
    found = client.get_by_id(delete['id'])
    assert not found
    # Assert that the task still exists
    found_task = client.get_by_id(task_obj['id'])
    assert found_task and found_task['projectId'] == client.state['inbox_id']
    # Delete the task
    client.task.delete(found_task['id'])


def test_delete_list_preserve_tasks_specified_new_list(client):
    """Tests deleting a list and preserving the tasks in a list that is not inbox"""
    list1 = client.list.create(str(uuid.uuid4()))
    list2 = client.list.create(str(uuid.uuid4()))
    # Add a task to list2
    task1 = client.task.create(str(uuid.uuid4()), list_id=list2['id'])
    delete = client.list.delete(list1['id'], preserve_tasks=True, move_to_list=list2['id'])
    assert not client.get_by_id(delete['id'])  # Make sure that the list doesn't exist
    assert client.get_by_id(list2['id'])
    task1_obj = client.get_by_id(task1['id'])
    assert task1_obj['projectId'] == list2['id']
    client.list.delete(list2['id'])  # Normal deletion deletes the task
    assert not client.get_by_id(task1['id'])


def test_delete_list_preserve_tasks_specified_inbox(client):
    """Tests deleting a list and saving the tasks if the move location is the inbox"""
    list1 = client.list.create(str(uuid.uuid4()))
    # Add a task to list1
    task1 = client.task.create(str(uuid.uuid4()), list_id=list1['id'])
    delete = client.list.delete(list1['id'], preserve_tasks=True, move_to_list=client.state['inbox_id'])
    assert not client.get_by_id(delete['id'])  # Make sure that the list doesn't exist
    task1_obj = client.get_by_id(task1['id'])
    assert task1_obj['projectId'] == client.state['inbox_id']
    client.task.delete(task1['id'])  # Cant delete inbox so just delete the task directly


def test_wrong_list_type(client):
    """Tests wrong list type entered"""
    type = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.list.create('List Name', list_type=type)


def test_create_list_random_color(client):
    """Tests creating a list with a random color"""
    name = str(uuid.uuid4())
    list_obj = client.list.create(name)  # No color specify will create random
    assert list_obj['color'] is not None
    client.list.delete(list_obj['id'])


def test_create_list_no_color(client):
    """Tests creating a list with no color"""
    name = str(uuid.uuid4())
    list_ = client.list.create(name, color=None)
    assert list_['color'] is None
    client.list.delete(list_['id'])


def test_wrong_hex_string_input(client):
    """Tests wrong input for hex color"""
    fail = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.list.create('', color=fail)


def test_wrong_hex_string_input_2(client):
    """Tests another wrong input for hex color"""
    fail = "#DD730CDD"
    with pytest.raises(ValueError):
        client.list.create('', color=fail)


def test_archive_list_success(client):
    # Create a test list
    name = str(uuid.uuid4())
    task = client.list.create(name)
    # Archive the test list
    archive = client.list.archive(task['id'])
    archive = client.get_by_id(archive['id'])
    assert archive['closed'] is True
    # Delete the test list
    client.list.delete(archive['id'])


def test_archive_list_failure(client):
    name = str(uuid.uuid4())
    with pytest.raises(KeyError):
        client.list.archive(name)


def test_create_list_folder(client):
    """List should be created and exist in client.state['list_folders']"""
    name = str(uuid.uuid4())
    response = client.list.create_folder(name)
    assert response
    client.list.delete_folder(response['id'])


def test_delete_list_folder(client):
    """Test Deletion of an already created folder"""
    name = str(uuid.uuid4())
    response = client.list.create_folder(name)
    deletion = client.list.delete_folder(response['id'])
    obj = client.get_by_id(deletion['id'], search='list_folders')
    assert not obj


def test_delete_list_folder_fail(client):
    """Test failed deletion of a non existent folder"""
    folder_id = str(uuid.uuid4())
    with pytest.raises(KeyError):
        client.list.delete_folder(folder_id)


def test_non_deletion_of_grouped_tasks(client):
    """Asserts that if a parent folder is deleted the lists are not deleted"""
    parent = client.list.create_folder(str(uuid.uuid4()))
    child1 = client.list.create(str(uuid.uuid4()), folder_id=parent['id'])
    child2 = client.list.create(str(uuid.uuid4()), folder_id=parent['id'])
    client.list.delete_folder(parent['id'])
    obj = client.get_by_id(child1['id'])
    obj2 = client.get_by_id(child2['id'])
    assert obj and obj2
    client.list.delete(obj['id'])
    client.list.delete(obj2['id'])


def test_update_list_folder(client):
    """Tests that updating list folder properties works"""
    parent = client.list.create_folder(str(uuid.uuid4()))
    parent['name'] = 'Changed Name'
    updated = client.list.update_folder(parent['id'])
    updated_obj = client.get_by_id(updated['id'])
    assert updated_obj['name'] == 'Changed Name'
    client.list.delete_folder(updated['id'])
