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
    get_object = client.get_by_id(task, search_key='lists')
    assert get_object['name'] == name
    client.list.delete(task)


def test_update_success(client):
    """Tests updating an already existing list"""
    name = str(uuid.uuid4())
    task = client.list.create(name)
    get_object = client.get_by_id(task, search_key='lists')
    assert get_object['name'] == name
    update_name = str(uuid.uuid4())
    get_object['name'] = update_name
    task2 = client.list.update(get_object['id'])
    get_object2 = client.get_by_id(task2, search_key='lists')
    assert get_object2['name'] == update_name
    assert get_object['id'] == get_object2['id']
    assert get_object['id'] == task2
    client.list.delete(task2)


def test_create_list_type_note_success(client):
    """Tests creating a list with type note"""
    name = str(uuid.uuid4())
    color = "#b20000"
    list_type = 'NOTE'
    task = client.list.create(name, color, list_type)
    my_object = client.get_by_id(task, search_key='lists')
    assert my_object
    client.list.delete(task)


def test_create_list_duplicate_failure(client):
    """Tests no list creation if the same name already exists"""
    name = str(uuid.uuid4())
    duplicate_name = name
    task = client.list.create(name)
    with pytest.raises(ValueError):
        client.list.create(duplicate_name)
    client.list.delete(task)


def test_delete_list_pass(client):
    """Tests list is properly deleted"""
    # Get id for 'Created List From Python'
    name = str(uuid.uuid4())
    name2 = str(uuid.uuid4())
    task1 = client.list.create(name)
    task2 = client.list.create(name2)
    # Delete List
    task1 = client.list.delete(task1)
    task2 = client.list.delete(task2)
    obj1 = client.get_by_id(task1)
    obj2 = client.get_by_id(task2)
    assert not obj1
    assert not obj2


def test_delete_list_fail(client):
    """Tests deletion will not occur if list name does not exist"""
    list_id = str(uuid.uuid4())
    with pytest.raises(KeyError):
        client.list.delete(list_id)


def test_wrong_list_type(client):
    """Tests wrong list type entered"""
    type = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.list.create('List Name', list_type=type)


def test_wrong_hex_string_input(client):
    """Tests wrong input for hex color"""
    fail = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.list.create('', color_id=fail)


def test_wrong_hex_string_input_2(client):
    """Tests another wrong input for hex color"""
    fail = "#DD730CDD"
    with pytest.raises(ValueError):
        client.list.create('', color_id=fail)


def test_archive_list_success(client):
    # Create a test list
    name = str(uuid.uuid4())
    task = client.list.create(name)
    # Archive the test list
    archive = client.list.archive(task)
    obj = client.get_by_id(archive)
    assert obj['closed'] is True
    # Delete the test list
    client.list.delete(archive)


def test_archive_list_failure(client):
    name = str(uuid.uuid4())
    with pytest.raises(KeyError):
        client.list.archive(name)


def test_create_list_folder(client):
    """List should be created and exist in client.list_groups"""
    name = str(uuid.uuid4())
    response = client.list.create_folder(name)
    obj = client.get_by_id(response)
    assert obj
    client.list.delete_folder(response)


def test_delete_list_folder(client):
    """Test Deletion of an already created folder"""
    name = str(uuid.uuid4())
    response = client.list.create_folder(name)
    deletion = client.list.delete_folder(response)
    obj = client.get_by_id(deletion, search_key='list_folders')
    assert not obj


def test_delete_list_folder_fail(client):
    """Test failed deletion of a non existent folder"""
    folder_id = str(uuid.uuid4())
    with pytest.raises(KeyError):
        client.list.delete_folder(folder_id)


def test_non_deletion_of_grouped_tasks(client):
    """Asserts that if a parent folder is deleted the lists are not deleted"""
    parent = client.list.create_folder(str(uuid.uuid4()))
    child1 = client.list.create(str(uuid.uuid4()), folder_id=parent)
    child2 = client.list.create(str(uuid.uuid4()), folder_id=parent)
    client.list.delete_folder(parent)
    obj = client.get_by_id(child1)
    obj2 = client.get_by_id(child2)
    assert obj and obj2
    client.list.delete(obj['id'])
    client.list.delete(obj2['id'])


def test_update_list_folder(client):
    """Tests that updating list folder properties works"""
    parent = client.list.create_folder(str(uuid.uuid4()))
    obj = client.get_by_id(parent)
    obj['name'] = 'Changed Name'
    updated = client.list.update_folder(parent)
    updated_obj = client.get_by_id(updated)
    assert updated_obj['name'] == 'Changed Name'
    client.list.delete_folder(updated)
