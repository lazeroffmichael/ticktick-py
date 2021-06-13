"""
Testing module for ListManager class
"""
import pytest
import uuid
from ticktick.helpers.hex_color import generate_hex_color


def test_builder_type_errors(client):
    with pytest.raises(TypeError):
        client.project.builder(3434)  # Invalid name type
    with pytest.raises(TypeError):
        client.project.builder('', color=453535)  # Invalid color type
    with pytest.raises(TypeError):
        client.project.builder('', project_type=3424)  # Invalid project type
    with pytest.raises(TypeError):
        client.project.builder('', folder_id=34234)  # Invalid folder id type


def test_builder_value_errors(client):
    name = str(uuid.uuid4())
    project = client.project.create(name)
    with pytest.raises(ValueError):
        client.project.builder(name)
    client.project.delete(project['id'])
    with pytest.raises(ValueError):
        client.project.builder('', project_type='yeah this does not exist')
    with pytest.raises(ValueError):
        client.project.builder('', color='Invalid')


def test_builder_success(client):
    project_name = str(uuid.uuid4())
    # Just project name
    project = client.project.builder(project_name)
    assert project['name'] == project_name and project['groupId'] is None and project['kind']
    color = generate_hex_color()
    project = client.project.builder(project_name, color=color)
    assert project['color'] == color


def test_create_list_success(client):
    """Tests creating a list and having it populate the class list dictionary"""
    name = str(uuid.uuid4())
    color = "#e070ff"
    task = client.project.create(name, color)
    assert task['name'] == name
    assert task['color'] == color
    assert task['groupId'] is None
    client.project.delete(task['id'])


def test_create_list_multiple(client):
    name1 = str(uuid.uuid4())
    name2 = str(uuid.uuid4())
    pro1 = client.project.builder(name1)
    pro2 = client.project.builder(name2)
    projects = client.project.create([pro1, pro2])
    try:
        assert client.get_by_id(projects[0]['id'])
        assert client.get_by_id(projects[1]['id'])
        assert projects[0]['name'] == name1
        assert projects[1]['name'] == name2
    except:
        client.project.delete([projects[0]['id'], projects[1]['id']])
        assert False
    else:
        client.project.delete([projects[0]['id'], projects[1]['id']])


def test_update_success(client):
    """Tests updating an already existing list"""
    name = str(uuid.uuid4())
    task = client.project.create(name)
    assert task['name'] == name
    update_name = str(uuid.uuid4())
    task['name'] = update_name
    task2 = client.project.update(task)
    assert task2['name'] == update_name
    client.project.delete(task2['id'])


def test_update_multiple_success(client):
    p1 = client.project.builder(str(uuid.uuid4()))
    p2 = client.project.builder(str(uuid.uuid4()))
    p3 = client.project.builder(str(uuid.uuid4()))
    projects = client.project.create([p1, p2, p3])
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    u3 = str(uuid.uuid4())
    projects[0]['name'] = u1
    projects[1]['name'] = u2
    projects[2]['name'] = u3
    ids = [x['id'] for x in projects]
    updated = client.project.update(projects)
    try:
        assert updated[0]['name'] == u1
        assert updated[1]['name'] == u2
        assert updated[2]['name'] == u3
    except:
        client.project.delete(ids)
        assert False
    else:
        client.project.delete(ids)


def test_create_list_type_note_success(client):
    """Tests creating a list with type note"""
    name = str(uuid.uuid4())
    color = "#b20000"
    list_type = 'NOTE'
    task = client.project.create(name, color, list_type)
    assert task['kind'] == list_type
    client.project.delete(task['id'])


def test_create_list_duplicate_failure(client):
    """Tests no list creation if the same name already exists"""
    name = str(uuid.uuid4())
    duplicate_name = name
    task = client.project.create(name)
    with pytest.raises(ValueError):
        client.project.create(duplicate_name)
    client.project.delete(task['id'])


def test_delete_type_error(client):
    ids = 44534
    with pytest.raises(TypeError):
        client.project.delete(ids)
    with pytest.raises(TypeError):
        client.project.delete({})


def test_delete_value_error(client):
    ids = '358397459835'
    with pytest.raises(ValueError):
        client.project.delete(ids)


def test_single_delete(client):
    name = str(uuid.uuid4())
    task1 = client.project.create(name)
    deletion = client.project.delete(task1['id'])
    assert task1 == deletion
    assert not client.get_by_id(task1['id'])


def test_delete_list_pass_multiple(client):
    """Tests list is properly deleted"""
    # Get id for 'Created List From Python'
    name = str(uuid.uuid4())
    name2 = str(uuid.uuid4())
    task1 = client.project.create(name)
    task2 = client.project.create(name2)
    # Delete List
    delete = [task1['id'], task2['id']]
    delete = client.project.delete(delete)
    assert task1 == delete[0]
    assert task2 == delete[1]
    assert len(delete) == 2
    assert delete[0] == task1
    assert delete[1] == task2
    task1 = client.get_by_id(task1['id'])
    task2 = client.get_by_id(task2['id'])
    assert not task1
    assert not task2


def test_delete_list_pass_single_with_task(client):
    project = client.project.create(str(uuid.uuid4()))
    task = {'title': 'Hello', "projectId": project['id']}
    task = client.task.create(task)
    assert task['projectId'] == project['id']
    deleted = client.project.delete(project['id'])
    assert deleted == project
    assert not client.get_by_id(task['id'])
    assert not client.get_by_id(project['id'])


def test_delete_list_pass_multiple_with_tasks(client):
    project = client.project.create(str(uuid.uuid4()))
    task1 = {'title': 'Hello', 'projectId': project['id']}
    task1 = client.task.create(task1)
    task2 = {'title': 'Hello', 'projectId': project['id']}
    task2 = client.task.create(task2)
    task3 = {'title': 'Hello', 'projectId': project['id']}
    task3 = client.task.create(task3)
    deleted = client.project.delete(project['id'])
    assert deleted == project
    assert not client.get_by_id(task1['id'])
    assert not client.get_by_id(task2['id'])
    assert not client.get_by_id(task3['id'])
    assert not client.get_by_id(project['id'])


def test_wrong_list_type(client):
    """Tests wrong list type entered"""
    type = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.project.create('List Name', project_type=type)


def test_create_list_random_color(client):
    """Tests creating a list with a random color"""
    name = str(uuid.uuid4())
    list_obj = client.project.create(name)  # No color specify will create random
    assert list_obj['color'] is not None
    client.project.delete(list_obj['id'])


def test_create_list_no_color(client):
    """Tests creating a list with no color"""
    name = str(uuid.uuid4())
    list_ = client.project.create(name, color=None)
    assert list_['color'] is None
    client.project.delete(list_['id'])


def test_wrong_hex_string_input(client):
    """Tests wrong input for hex color"""
    fail = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.project.create('', color=fail)


def test_wrong_hex_string_input_2(client):
    """Tests another wrong input for hex color"""
    fail = "#DD730CDD"
    with pytest.raises(ValueError):
        client.project.create('', color=fail)


def test_archive_list_success(client):
    # Create a test list
    name = str(uuid.uuid4())
    task = client.project.create(name)
    # Archive the test list
    archive = client.project.archive(task['id'])
    archive = client.get_by_id(archive['id'])
    assert archive['closed'] is True
    # Delete the test list
    client.project.delete(archive['id'])


def test_archive_list_success_multiple(client):
    n1 = str(uuid.uuid4())
    n2 = str(uuid.uuid4())
    p1 = client.project.builder(n1)
    p2 = client.project.builder(n2)
    projects = client.project.create([p1, p2])
    ids = [x['id'] for x in projects]
    # Archive
    archive = client.project.archive(ids)
    # Make sure return ordering is correct
    assert archive[0]['name'] == n1 and archive[0]['closed'] is True
    assert archive[1]['name'] == n2 and archive[1]['closed'] is True
    client.project.delete(ids)


def test_archive_list_failure(client):
    name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.project.archive(name)
    with pytest.raises(TypeError):
        client.project.archive(12313)
    with pytest.raises(TypeError):
        client.project.archive({})


def test_create_list_folder(client):
    """List should be created and exist in client.state['project_folders']"""
    name = str(uuid.uuid4())
    response = client.project.create_folder(name)
    assert response['name'] == name
    client.project.delete_folder(response['id'])


def test_create_list_folder_multiple(client):
    n1 = str(uuid.uuid4())
    n2 = str(uuid.uuid4())
    folders = client.project.create_folder([n1, n2])
    assert folders[0]['name'] == n1
    assert folders[1]['name'] == n2
    ids = [x['id'] for x in folders]
    client.project.delete_folder(ids)


def test_delete_list_folder(client):
    """Test Deletion of an already created folder"""
    name = str(uuid.uuid4())
    response = client.project.create_folder(name)
    deletion = client.project.delete_folder(response['id'])
    obj = client.get_by_id(deletion['id'], search='project_folders')
    assert not obj


def test_delete_list_folder_multiple(client):
    n1 = str(uuid.uuid4())
    n2 = str(uuid.uuid4())
    n3 = str(uuid.uuid4())
    folders = client.project.create_folder([n1, n2, n3])
    ids = [x['id'] for x in folders]
    deletion = client.project.delete_folder(ids)
    for i in ids:
        assert not client.get_by_id(i, search='project_folders')
    assert deletion[0]['id'] == ids[0]
    assert deletion[1]['id'] == ids[1]
    assert deletion[2]['id'] == ids[2]


def test_delete_list_folder_fail(client):
    """Test failed deletion of a non existent folder"""
    with pytest.raises(TypeError):
        client.project.delete_folder(12323)
    with pytest.raises(TypeError):
        client.project.delete_folder({})
    with pytest.raises(ValueError):
        client.project.delete_folder(' ')
    with pytest.raises(ValueError):
        client.project.delete_folder([' '])


def test_non_deletion_of_grouped_tasks(client):
    """Asserts that if a parent folder is deleted the lists are not deleted"""
    parent = client.project.create_folder(str(uuid.uuid4()))
    child1 = client.project.create(str(uuid.uuid4()), folder_id=parent['id'])
    child2 = client.project.create(str(uuid.uuid4()), folder_id=parent['id'])
    client.project.delete_folder(parent['id'])
    obj = client.get_by_id(child1['id'])
    obj2 = client.get_by_id(child2['id'])
    assert obj and obj2
    client.project.delete(obj['id'])
    client.project.delete(obj2['id'])


def test_update_list_folder(client):
    """Tests that updating list folder properties works"""
    parent = client.project.create_folder(str(uuid.uuid4()))
    changed_name = str(uuid.uuid4())
    parent['name'] = changed_name
    updated = client.project.update_folder(parent)
    updated_obj = client.get_by_id(updated['id'])
    assert updated_obj['name'] == changed_name
    client.project.delete_folder(updated['id'])


def test_update_list_folder_multiple(client):
    p1 = str(uuid.uuid4())
    p2 = str(uuid.uuid4())
    p3 = str(uuid.uuid4())
    p = [p1, p2, p3]
    folders = client.project.create_folder(p)
    n1 = str(uuid.uuid4()).upper()
    n2 = str(uuid.uuid4())
    n3 = str(uuid.uuid4()).upper()
    folders[0]['name'] = n1
    folders[1]['name'] = n2
    folders[2]['name'] = n3
    updated = client.project.update_folder(folders)
    ids = [x['id'] for x in updated]
    assert updated[0]['name'] == n1
    assert updated[1]['name'] == n2
    assert updated[2]['name'] == n3
    client.project.delete_folder(ids)


def test_update_folders_fail(client):
    with pytest.raises(TypeError):
        client.project.update_folder('')
    with pytest.raises(TypeError):
        client.project.update_folder(34324)
